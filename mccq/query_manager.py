import re
import typing

from mccq import errors, utils
from mccq.data_node import DataNode
from mccq.query_arguments import QueryArguments
from mccq.typedefs import IterableOfStrings, TupleOfStrings
from mccq.version_database import VersionDatabase

# map of version names to command results
# example: `{'18w01a': ('tag <targets> add <tag>', 'tag <targets> remove <tag>')}`
QueryResults = typing.Dict[str, TupleOfStrings]


class QueryManager:
    def __init__(
            self,
            database: VersionDatabase,
            show_versions: IterableOfStrings,
    ):
        self.database = database
        self.show_versions: TupleOfStrings = tuple(show_versions)

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
        requested_versions = arguments.versions or self.show_versions

        # make sure at least one version was requested
        if not requested_versions:
            raise errors.NoVersionRequested()

        # filter out unavailable versions
        filtered_versions = self.database.filter_versions(requested_versions)

        # make sure at least one of the requested versions is available
        if not filtered_versions:
            raise errors.NoVersionsAvailable(requested_versions)

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
        return self.results_from_arguments(utils.parse_query_arguments(command))
