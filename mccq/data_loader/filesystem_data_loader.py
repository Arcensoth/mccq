import json
import logging
import os

from mccq.data_loader.abc.data_loader import DataLoader
from mccq.typedefs import TupleOfStrings

log = logging.getLogger(__name__)


class FilesystemDataLoader(DataLoader):
    def load(self, components: TupleOfStrings) -> dict:
        path = os.path.join(*components)
        log.info(f'Loading commands from filesystem: {path}')
        with open(path) as fp:
            raw = json.load(fp)
        return raw

    def load_version(self, components: TupleOfStrings) -> str:
        path = os.path.join(*components)
        log.info(f'Loading version from filesystem: {path}')
        with open(path) as fp:
            raw = str(fp.readline()).strip()
        return raw
