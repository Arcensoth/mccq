import logging
import os
import shlex
import sys
import urllib.parse

from mccq import errors
from mccq.argument_parser import ArgumentParser
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
    '-l', '--log', default='WARNING', help='log level')

startup_args = startup_parser.parse_args(shlex.split(' '.join(sys.argv[1:])))

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
print('Enter a Minecraft command query, or "exit" to leave.')

while True:
    try:
        command = input('> ')

    except KeyboardInterrupt:
        print()
        break

    if command.startswith('\\'):
        try:
            meta_command = command[1:]
            meta_args = shlex.split(meta_command)
            meta_root = meta_args[0]

            if meta_root in {'x', 'exit'}:
                break

            elif meta_root in {'r', 'reload'}:
                qm.database.reload()

            elif meta_root in {'s', 'show'}:
                qm.show_versions = tuple(meta_args[1:])

        except Exception as ex:
            print(f'Error: {ex}')

    elif command:
        try:
            for version, commands in qm.results(command).items():
                print(f'# {version}')
                for command in commands:
                    print(command)

        except errors.NoVersionRequested:
            print('No versions provided, use \\s to set the default(s).')

        except Exception as ex:
            print(f'Error: {ex}')

print('Goodbye!')
