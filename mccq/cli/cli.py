import logging
import os
import shlex
import sys
import urllib.parse

from mccq.argument_parser import ArgumentParser
from mccq.cli.loop import cli_loop
from mccq.query_manager import QueryManager
from mccq.version_database import LOADER_MAP, VersionDatabase

# TODO other os, edge cases
local_database = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', '.minecraft', 'versions')

startup_parser = ArgumentParser(
    'mccq',
    description='Minecraft command query program. Inspired by the in-game help command, with added features like '
                'version reporting and expandable regex search.')

startup_parser.add_argument(
    '-s', '--show_versions', action='append', default=[], help='which version(s) to render by default (repeatable)')

startup_parser.add_argument(
    '-d', '--database_uri', default=local_database, help='the uri from where versions will be loaded')

startup_parser.add_argument(
    '-l', '--log', default=logging.WARNING, help='log level')

try:
    startup_args = startup_parser.parse_args(shlex.split(' '.join(sys.argv[1:])))
except:
    sys.exit()

logging.basicConfig(level=startup_args.log)

log = logging.getLogger(__name__)

show_versions = startup_args.show_versions
database_uri = startup_args.database_uri

# the uri scheme determines from where to load the data
uri_scheme = urllib.parse.urlparse(database_uri).scheme

# fallback to filesystem loader
uri_scheme = uri_scheme if uri_scheme in LOADER_MAP else 'file'

db = VersionDatabase(
    uri=database_uri,
    loader=uri_scheme)

qm = QueryManager(
    database=db,
    show_versions=show_versions)


print('[::] Minecraft Command Query CLI [::]')

# attempt to load extra features like navigation and autocompletion
try:
    import readline
    from mccq.cli.completer import CLICompleter

    cc = CLICompleter(qm)

    readline.set_completer_delims(' \t\n')
    readline.parse_and_bind('tab: complete')
    readline.set_completer(cc.complete)

    print('Navigation and autocompletion are available on the current system.')

except:
    pass

print('Enter a Minecraft command query, or "exit" to leave.')

cli_loop(qm)

print('Goodbye!')
