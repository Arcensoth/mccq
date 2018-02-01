import json
import logging
import os
import re
import typing

from mccq import errors, utils
from mccq.mccq_arguments import MCCQArguments
from mccq.data.data_node import MCCQDataNode
from mccq.data.parsers.abc.mccq_data_parser import MCCQDataParser
from mccq.data.parsers.parsers import PARSERS
from mccq.typedefs import IterableOfStrings, SetOfStrings, TupleOfStrings

log = logging.getLogger(__name__)

# map of version names to remaining `MCCQ.load()` method arguments
# example: `{'18w01a': {'parser': 'v1', 'path': './commands.18w01a.json'}}`
VersionsDefinition = typing.Dict[str, dict]

# map of version names to command results
# example: `{'18w01a': ('tag <targets> add <tag>', 'tag <targets> remove <tag>')}`
MCCQResults = typing.Dict[str, TupleOfStrings]


class MCCQ:
    def __init__(
            self,
            versions_storage: str,
            versions_definition: VersionsDefinition,
            show_versions: IterableOfStrings,
    ):
        self.versions_storage = versions_storage
        self.show_versions: TupleOfStrings = tuple(show_versions)

        self.data: typing.Dict[str, MCCQDataNode] = {}

        self.reload(versions_definition)

    def _command_lines_from_node(self, arguments: MCCQArguments, node: MCCQDataNode) -> IterableOfStrings:
        command = node.command_t if arguments.showtypes else node.command
        collapsed = (node.collapsed_t if arguments.showtypes else node.collapsed) or command

        # only produce relevant commands:
        #   - all executable commands: `scoreboard players list`, `scoreboard players list <target>`
        #   - all chainable (redirect) commands: `execute as <entity> -> execute`
        #   - some exceptional cases: `execute run ...`
        if command and node.relevant:
            yield command

        # determine whether to continue searching any existing children for subcommands
        # if any of the following are true, continue searching:
        #   1. explode override flag is set
        #   2. capacity has not been reached
        #   3. only one child/subcommand to expand
        if node.children and (
                arguments.explode
                or (node.population <= arguments.capacity)
                or len(node.children) == 1
        ):
            for child in node.children.values():
                yield from self._command_lines_from_node(arguments, child)

        # otherwise produce a collapsed form
        # be careful not to produce duplicate results for "relevant" nodes
        elif collapsed and not node.relevant:
            yield collapsed

    def _command_lines_recursive(self, arguments: MCCQArguments, node: MCCQDataNode, index: int) -> IterableOfStrings:
        # determine the current search term
        token = arguments.command[index] if len(arguments.command) > index else None

        # use regex to search for the subcommand/argument name in the patternized token
        # special case: dot matches all
        search_children = node.children if token == '.' else {
            child_key: child for child_key, child in (node.children or {}).items()
            if re.match(f'^{token}$', child_key, re.IGNORECASE)
        }

        # branch: search all matching children recursively (depth-first) for subcommands
        if search_children:
            for child_key, child in search_children.items():
                yield from self._command_lines_recursive(arguments, child, index + 1)

        # leaf: no children to search and tokens depleted; start producing commands from here
        elif not token:
            yield from self._command_lines_from_node(arguments, node)

        # at this point 'else' means there are still tokens to search, so the query goes deeper than the current node
        # and we can just ignore it

    def commands_for_version(self, version: str, arguments: MCCQArguments) -> TupleOfStrings:
        root_node = self.data.get(version)

        # make sure the version is loaded
        if not root_node:
            raise errors.NoSuchVersionMCCQError(version)

        # make sure a command was provided
        if len(arguments.command) > 0:
            base_command = arguments.command[0]
        else:
            raise errors.MissingCommandMCCQError()

        # make sure the base command is valid
        try:
            base_node = root_node.children[base_command]
        except Exception as ex:
            raise errors.NoSuchCommandMCCQError(base_command) from ex

        # we already did some work here; bypass the root node and start at the base command node
        return tuple(self._command_lines_recursive(arguments, base_node, index=1))

    def load(self, version: str, parser: typing.Union[str, MCCQDataParser], path: str = None):
        # prioritize an explicit path
        data_path = path if path else os.path.join(
            self.versions_storage, version, 'generated', 'reports', 'commands.json')

        log.info('Loading commands for version {} from: {}'.format(version, data_path))

        # load the data file
        try:
            with open(data_path) as fp:
                raw = json.load(fp)
        except Exception as ex:
            raise errors.DataFileFailureMCCQError(version, data_path) from ex

        # if parser is a str, check for pre-existing singleton
        if isinstance(parser, str):
            parser = PARSERS.get(parser)
            if not parser:
                raise errors.UnknownParserMCCQError(parser)

        # parse and insert data
        try:
            self.data[version] = parser.parse(raw)
        except Exception as ex:
            raise errors.ParserFailureMCCQError(version) from ex

    def reload(self, versions_definition: VersionsDefinition):
        # clear existing data
        self.data = {}

        # load versions, one by one
        for version, definition in versions_definition.items():
            self.load(version, **definition)

        log.info('Loaded commands for {} versions: {}'.format(
            len(self.available_versions), ', '.join(self.available_versions)))

    def results_from_arguments(self, arguments: MCCQArguments) -> MCCQResults:
        requested_versions = arguments.versions or self.show_versions

        # note that using a set ruins the order
        valid_versions = set(requested_versions).intersection(self.available_versions)

        # make sure at least one of the requested versions is available
        if not valid_versions:
            raise errors.NoVersionsAvailableMCCQError(requested_versions)

        # reorder the versions
        final_versions = (version for version in requested_versions if version in valid_versions)

        # build results
        # make sure to handle version-specific errors
        results = {}
        for version in final_versions:
            try:
                commands = self.commands_for_version(version, arguments)

            # ignore unknown versions and commands because we may have other results
            except (errors.NoSuchVersionMCCQError, errors.NoSuchCommandMCCQError):
                continue

            # let this one through: errors.MissingCommandMCCQError
            # because if there's no command, the version doesn't matter

            # don't include versions with no results
            if commands:
                results[version] = commands

        return results

    def results(self, command: str) -> MCCQResults:
        return self.results_from_arguments(utils.parse_mccq_arguments(command))

    @property
    def available_versions(self) -> SetOfStrings:
        return set(self.data.keys())
