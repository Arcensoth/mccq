import json
import logging
import urllib.request

from mccq.data_loader.abc.data_loader import DataLoader
from mccq.typedefs import TupleOfStrings

log = logging.getLogger(__name__)


class InternetDataLoader(DataLoader):
    def load(self, components: TupleOfStrings) -> dict:
        path = '/'.join(components)
        log.info(f'Loading commands from internet: {path}')
        response = urllib.request.urlopen(path)
        content = response.read().decode('utf8')
        raw = json.loads(content)
        return raw

    def load_version(self, components: TupleOfStrings) -> str:
        path = '/'.join(components)
        log.info(f'Loading version from internet: {path}')
        response = urllib.request.urlopen(path)
        content = response.readline().decode('utf8')
        raw = str(content).strip()
        return raw
