import re
import shlex
import typing

from mccq import errors
from mccq.argument_parser import ArgumentParser
from mccq.data_node import DataNode
from mccq.query_arguments import QueryArguments
from mccq.typedefs import IterableOfStrings, TupleOfStrings
from mccq.version_database import VersionDatabase

# map of version names to command results
# example: `{'18w01a': ('tag <targets> add <tag>', 'tag <targets> remove <tag>')}`
QueryResults = typing.Dict[str, TupleOfStrings]


class QueryManager:
    ARGUMENT_PARSER = ArgumentParser(
        'mccq',
        description='Minecraft command query program. Inspired by the in-game help command, with added features like'
                    'multiple version support and expandable regex search.',
        add_help=False)

    ARGUMENT_PARSER.add_argument(
        '-t', '--showtypes', action='store_true', help='whether to show argument types')

    ARGUMENT_PARSER.add_argument(
        '-e', '--explode', action='store_true', help='whether to expand all subcommands, regardless of capacity')

    ARGUMENT_PARSER.add_argument(
        '-c', '--capacity', type=int, default=3, help='maximum number of subcommands to render before collapsing')

    ARGUMENT_PARSER.add_argument(
        '-v', '--version', action='append', default=[], help='which version(s) to use for the command (repeatable)')

    ARGUMENT_PARSER.add_argument(
        'command', nargs='+', help='the command query')

    def __init__(
            self,
            database: VersionDatabase,
            show_versions: IterableOfStrings,
    ):
        self.database = database
        self.show_versions: TupleOfStrings = tuple(show_versions)

    @staticmethod
    def parse_query_arguments(command: str) -> QueryArguments:
        try:
            # split into tokens using shell-like syntax (preserve quoted substrings)
            parsed_args = QueryManager.ARGUMENT_PARSER.parse_args(shlex.split(command))

            # return an object representation
            return QueryArguments(
                command=tuple(parsed_args.command),  # immutable copy
                showtypes=parsed_args.showtypes,
                explode=parsed_args.explode,
                capacity=parsed_args.capacity,
                versions=tuple(parsed_args.version),  # duplicate versions are meaningless
            )

        except Exception as ex:
            raise errors.ArgumentParserFailed(command) from ex

    def _trimed_tree_recursive(self, arguments: QueryArguments, node: DataNode, index: int) \
            -> typing.Union[DataNode, None]:
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
            trimmed_children = {}

            for child_key, child in search_children.items():
                trimmed_child = self._trimed_tree_recursive(arguments, child, index + 1)

                if trimmed_child:
                    trimmed_children[child_key] = trimmed_child

            if trimmed_children:
                # return a new node with trimmed children
                return DataNode(
                    relevant=node.relevant,
                    population=node.population,
                    key=node.key,
                    command=node.command,
                    command_t=node.command_t,
                    argument=node.argument,
                    argument_t=node.argument_t,
                    collapsed=node.collapsed,
                    collapsed_t=node.collapsed_t,
                    children=trimmed_children)

        # leaf: no children to search and tokens depleted; return a childless copy of the node
        elif not token:
            return DataNode(
                relevant=node.relevant,
                population=node.population,
                key=node.key,
                command=node.command,
                command_t=node.command_t,
                argument=node.argument,
                argument_t=node.argument_t,
                collapsed=node.collapsed,
                collapsed_t=node.collapsed_t)

        # at this point 'else' means there are still tokens to search, so the query goes deeper than the current node
        # and we can just ignore it

    def tree_for_version(self, version: str, arguments: QueryArguments) -> typing.Union[DataNode, None]:
        # build a trimmed tree containing only the nodes that match the given arguments
        root_node = self.database.get(version)
        return self._trimed_tree_recursive(arguments, root_node, index=0)

    def _command_lines_from_node(self, arguments: QueryArguments, node: DataNode) -> IterableOfStrings:
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

    def _command_lines_recursive(self, arguments: QueryArguments, node: DataNode, index: int) -> IterableOfStrings:
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

    def filter_versions(self, arguments: QueryArguments) -> TupleOfStrings:
        requested_versions = arguments.versions or self.show_versions

        # make sure at least one version was requested
        if not requested_versions:
            raise errors.NoVersionRequested()

        # filter out unavailable versions
        filtered_versions = self.database.filter_versions(requested_versions)

        # make sure at least one of the requested versions is available
        if not filtered_versions:
            raise errors.NoVersionsAvailable(requested_versions)

        return filtered_versions

    def commands_for_version(self, version: str, arguments: QueryArguments) -> TupleOfStrings:
        root_node = self.database.get(version)

        # make sure the version is loaded
        if not root_node:
            raise errors.NoSuchVersion(version)

        # make sure a command was provided
        if len(arguments.command) > 0:
            base_command = arguments.command[0]
        else:
            raise errors.MissingCommand()

        # make sure the base command is valid
        try:
            base_node = root_node.children[base_command]
        except Exception as ex:
            raise errors.NoSuchCommand(base_command) from ex

        # we already did some work here; bypass the root node and start at the base command node
        return tuple(self._command_lines_recursive(arguments, base_node, index=1))

    def results_from_arguments(self, arguments: QueryArguments) -> QueryResults:
        filtered_versions = self.filter_versions(arguments)

        # build results
        # make sure to handle version-specific errors
        results = {}
        for version in filtered_versions:
            try:
                commands = self.commands_for_version(version, arguments)

            # ignore unknown versions and commands because we may have other results
            except (errors.NoSuchVersion, errors.NoSuchCommand):
                continue

            # let this one through: errors.MissingCommand
            # because if there's no command, the version doesn't matter

            # don't include versions with no results
            if commands:
                results[version] = commands

        return results

    def results(self, command: str) -> QueryResults:
        return self.results_from_arguments(self.parse_query_arguments(command))
