import argparse
import json
import shlex
import sys

from mccq.mccq import MCCQ

startup_parser = argparse.ArgumentParser(
    'mccq',
    description='Minecraft command query program. Inspired by the in-game help command, with added features like '
                'version reporting and expandable regex search.')

startup_parser.add_argument(
    'config', help='the config file to load')

startup_args = startup_parser.parse_args(shlex.split(sys.argv))

config = json.load(startup_args.config)

mccq_instance = MCCQ(
    database=config.get('versions_storage'),
    versions=config.get('versions_definition'),
    show_versions=config.get('show_versions'),
)

command = input('>')
for version, commands in mccq_instance.results(command):
    print('# '.format(version))
    for command in commands:
        print(command)
    print()
