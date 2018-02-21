import shlex

from mccq import errors
from mccq.query_manager import QueryManager


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

                if meta_root in {'x', 'exit'}:
                    return

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
