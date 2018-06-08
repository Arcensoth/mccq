import logging
import typing
import urllib.parse

from mccq import errors
from mccq.data_loader.abc.data_loader import DataLoader
from mccq.data_loader.filesystem_data_loader import FilesystemDataLoader
from mccq.data_loader.internet_data_loader import InternetDataLoader
from mccq.data_parser.abc.data_parser import DataParser
from mccq.data_parser.v1_data_parser import V1DataParser
from mccq.node.data_node import DataNode
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


def find_loader(obj, uri) -> DataLoader:
    try:
        if obj is None:
            # auto-detect database source to instantiate an appropriate loader
            uri_scheme = urllib.parse.urlparse(uri).scheme
            return LOADER_MAP.get(uri_scheme, LOADER_MAP['file'])()

        elif isinstance(obj, str):
            return LOADER_MAP[obj]()

        elif isinstance(obj, DataLoader):
            return obj

    except Exception as ex:
        raise errors.InvalidLoader(obj) from ex


def find_parser(obj) -> DataParser:
    try:
        if obj is None:
            # default to the only available parser
            return PARSER_MAP['v1']()

        elif isinstance(obj, str):
            return PARSER_MAP[obj]()

        elif isinstance(obj, DataParser):
            return obj

    except Exception as ex:
        raise errors.InvalidParser(obj) from ex


class VersionDatabase:
    def __init__(
            self, uri: str, loader: LoaderGeneric = None, parser: ParserGeneric = None, version_file: str = None,
            whitelist: IterableOfStrings = ()):
        self.uri = uri
        self.version_file = version_file
        self.whitelist = set(whitelist)
        self.loader: DataLoader = find_loader(loader, uri)
        self.parser: DataParser = find_parser(parser)
        self._node_cache: typing.Dict[str, DataNode] = {}
        self._version_cache: typing.Dict[str, str] = {}

    def _load_actual_version(self, version: str) -> str:
        return self.loader.load_version((self.uri, version, self.version_file))

    def _load(self, version: str):
        components = (self.uri, version, *DATA_FILE_TAIL)

        try:
            actual_version = self._load_actual_version(version)
            self._version_cache[version] = actual_version
            log.info(f'Loading commands for version {version} (actual {actual_version}) with components: {components}')
        except:
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

    def get_actual_version(self, version: str) -> str:
        return self._version_cache.get(version)

    def reload(self):
        self._node_cache = {}
        self._version_cache = {}

    def get(self, version: str) -> DataNode:
        log.debug(f'Getting root node for version {version}')
        if version not in self._node_cache:
            log.info(f'Loading version {version} into cache')
            self._load(version)
        return self._node_cache[version]

    def put(self, version: str, root_node: DataNode):
        if self.whitelist and version not in self.whitelist:
            raise errors.VersionNotWhitelisted(version)
        self._node_cache[version] = root_node

    def filter_versions(self, requested_versions: IterableOfStrings) -> TupleOfStrings:
        # if no whitelist, everything is valid
        if not self.whitelist:
            return requested_versions
        # otherwise filter out versions that are not whitelisted
        available_versions = set(requested_versions).intersection(self.whitelist)
        # make sure to preserve order
        return tuple(version for version in requested_versions if version in available_versions)
