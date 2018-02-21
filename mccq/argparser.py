import argparse

ARGPARSER = argparse.ArgumentParser(
    'mccq',
    description='Minecraft command query program. Inspired by the in-game help command, with added features like'
                'multiple version support and expandable regex search.',
    add_help=False)

ARGPARSER.add_argument(
    '-t', '--showtypes', action='store_true', help='whether to show argument types')

ARGPARSER.add_argument(
    '-e', '--explode', action='store_true', help='whether to expand all subcommands, regardless of capacity')

ARGPARSER.add_argument(
    '-c', '--capacity', type=int, default=3, help='maximum number of subcommands to render before collapsing')

ARGPARSER.add_argument(
    '-v', '--version', action='append', default=[], help='which version(s) to use for the command (repeatable)')

ARGPARSER.add_argument(
    'command', nargs='+', help='the command query')
