import logging
import typing

from mccq import errors
from mccq.data_loader.abc.data_loader import DataLoader
from mccq.data_loader.filesystem_data_loader import FilesystemDataLoader
from mccq.data_loader.internet_data_loader import InternetDataLoader
from mccq.data_node import DataNode
from mccq.data_parser.abc.data_parser import DataParser
from mccq.data_parser.v1_data_parser import V1DataParser
from mccq.typedefs import IterableOfStrings, TupleOfStrings

log = logging.getLogger(__name__)

LoaderGeneric = typing.Union[str, DataLoader]
ParserGeneric = typing.Union[str, DataParser]

LOADER_MAP = {
    'file': FilesystemDataLoader,
    'http': InternetDataLoader,
    'https': InternetDataLoader
}

PARSER_MAP = {
    'v1': V1DataParser
}

DATA_FILE_TAIL = ('generated', 'reports', 'commands.json')


class VersionDatabase:
    DEFAULT_LOADER = 'file'
    DEFAULT_PARSER = 'v1'

    def __init__(
            self, uri: str, loader: LoaderGeneric = DEFAULT_LOADER, parser: ParserGeneric = DEFAULT_PARSER,
            whitelist: IterableOfStrings = ()):
        self.uri = uri
        self.whitelist = whitelist

        if isinstance(loader, str):
            loader_ctor = LOADER_MAP.get(loader)
            if not loader_ctor:
                raise errors.UnknownLoader(loader)
            loader = loader_ctor()

        self.loader: DataLoader = loader

        if isinstance(parser, str):
            parser_ctor = PARSER_MAP.get(parser)
            if not parser_ctor:
                raise errors.UnknownParser(parser)
            parser = parser_ctor()

        self.parser: DataParser = parser

        self._cache: typing.Dict[str, DataNode] = {}

        self.reload()

    def _load(self, version: str):
        components = (self.uri, version, *DATA_FILE_TAIL)

        log.info(f'Loading commands for version {version} with components: {components}')

        # load data from source
        try:
            raw = self.loader.load(components)
        except Exception as ex:
            raise errors.LoaderFailure(version) from ex

        # parse and insert data
        try:
            parsed = self.parser.parse(raw)
        except Exception as ex:
            raise errors.ParserFailure(version) from ex

        self.put(version, parsed)

    def reload(self):
        self._cache = {}

    def get(self, version: str) -> DataNode:
        log.debug(f'Getting root node for version {version}')
        if version not in self._cache:
            log.info(f'Loading version {version} into cache')
            self._load(version)
        return self._cache[version]

    def put(self, version: str, root_node: DataNode):
        if self.whitelist and version not in self.whitelist:
            raise errors.VersionNotWhitelisted(version)
        self._cache[version] = root_node

    def filter_versions(self, requested_versions) -> TupleOfStrings:
        # if no whitelist, everything is valid
        if not self.whitelist:
            return requested_versions
        # otherwise filter out versions that are not whitelisted
        available_versions = set(requested_versions).intersection(self.whitelist)
        # make sure to preserve order
        return (version for version in requested_versions if version in available_versions)
