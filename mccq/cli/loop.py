import logging
import shlex

from mccq import errors
from mccq.cli.meta import META_MAP
from mccq.query_manager import QueryManager

log = logging.getLogger(__name__)


def cli_loop(qm: QueryManager):
    while True:
        try:
            command = input('> ')

        except KeyboardInterrupt:
            print()
            return

        if command.startswith('\\'):
            try:
                meta_command = command[1:]
                meta_args = shlex.split(meta_command)
                meta_root = meta_args[0]

                if meta_root in META_MAP['exit']:
                    return

                elif meta_root in META_MAP['reload']:
                    qm.database.reload()

                elif meta_root in META_MAP['show']:
                    qm.show_versions = tuple(meta_args[1:])

                else:
                    raise ValueError('Invalid command', command)

            except Exception:
                print('Invalid command, please try again.')
                if log.isEnabledFor(logging.DEBUG):
                    log.exception('Error')

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
                if log.isEnabledFor(logging.DEBUG):
                    log.exception('Error')
