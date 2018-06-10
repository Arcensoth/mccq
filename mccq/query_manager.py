import re
import shlex
import typing

from mccq import errors
from mccq.argument_parser import ArgumentParser
from mccq.node.data_node import DataNode
from mccq.node.query_node import QueryNode
from mccq.query_arguments import QueryArguments
from mccq.typedefs import IterableOfStrings, TupleOfStrings
from mccq.version_database import VersionDatabase

# map of version names to command results
# example: `{'18w01a': ('tag <targets> add <tag>', 'tag <targets> remove <tag>')}`
QueryResults = typing.Dict[str, TupleOfStrings]


class QueryManager:
    ARGUMENT_PARSER = ArgumentParser(
        'mccq',
        description='Minecraft command query program. Inspired by the in-game help command, with added features like '
                    'version reporting and expandable regex search.',
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

    def _query_tree_recursive(self, arguments: QueryArguments, node: DataNode, index: int) \
            -> typing.Union[QueryNode, None]:
        # determine the current search term
        token = arguments.command[index] if len(arguments.command) > index else None

        # use regex to search for the subcommand/argument name in the patternized token
        # special case: dot matches all
        search_children = node.children if token == '.' else tuple(
            child for child in node.children
            if re.match(f'^{token}$', child.key, re.IGNORECASE)
        )

        # branch: search all matching children recursively (depth-first) for subcommands
        if search_children:
            query_children = tuple(item for item in (
                self._query_tree_recursive(arguments, child, index + 1) for child in search_children
            ) if item is not None)

            if query_children:
                # return a query node with the calculated subset of children
                return QueryNode(data_node=node, children=query_children)

        # leaf: no children to search and tokens depleted; return a childless query node
        # note that even though this is a recursive leaf, the contained data node may itself have children
        elif not token:
            return QueryNode(data_node=node)

        # at this point 'else' means there are still tokens to search, so the query goes deeper than the current node
        # and we can just ignore it

    def _commands_recursives(self, arguments: QueryArguments, node: DataNode) -> IterableOfStrings:
        command = node.command_t if arguments.showtypes else node.command
        collapsed = node.collapsed_t if arguments.showtypes else node.collapsed

        # render relevant commands:
        #   - all executable commands: `scoreboard players list`, `scoreboard players list <target>`
        #   - all chainable (redirect) commands: `execute as <entity> -> execute`
        #   - some exceptional cases: `execute run ...`
        if node.relevant:
            yield command

        # determine whether to continue searching any existing children for subcommands
        # if any of the following are true, continue searching:
        #   1. explode override flag is set
        #   2. capacity has not been reached
        #   3. only one child to search
        if node.children and (
                arguments.explode
                or (node.population <= arguments.capacity)
                or len(node.children) == 1
        ):
            for child in node.children:
                yield from self._commands_recursives(arguments, child)

        # otherwise render a collapsed form
        elif collapsed:
            yield collapsed

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

    def query_tree_for_version(self, version: str, arguments: QueryArguments) -> typing.Union[QueryNode, None]:
        # get the root data node and make sure the version is loaded
        root_data_node = self.database.get(version)
        if not root_data_node:
            raise errors.NoSuchVersion(version)

        # build a trimmed tree containing only the nodes that match the given arguments
        query_tree = self._query_tree_recursive(arguments, root_data_node, index=0)

        return query_tree

    def commands_for_version(self, version: str, arguments: QueryArguments) -> IterableOfStrings:
        # first build a result tree from the given arguments
        query_tree = self.query_tree_for_version(version, arguments)

        # proceed only if the query returned something
        if query_tree:
            # then check every branch and leaf for relevant commands
            # get all leaves of the query tree, and then all of the leaves of their corresponding data nodes
            for leaf in query_tree.leaves():
                yield from self._commands_recursives(arguments, leaf.data_node)

    def results_from_versions(self, versions: IterableOfStrings, arguments: QueryArguments) -> QueryResults:
        # ignore errors when multiple versions are specified
        # (not sure how else to handle this gracefully)
        results = {}
        for version in versions:
            try:
                commands = tuple(self.commands_for_version(version, arguments))

            # ignore errors because we may have other results
            except:
                continue

            # don't include versions with no results
            if commands:
                results[version] = commands

        return results

    def results_from_version(self, version: str, arguments: QueryArguments) -> QueryResults:
        # handle single version requests differently by allowing errors to propagate
        commands = tuple(self.commands_for_version(version, arguments))
        return {version: commands} if commands else {}

    def results_from_arguments(self, arguments: QueryArguments) -> QueryResults:
        filtered_versions = self.filter_versions(arguments)
        if len(filtered_versions) > 1:
            results = self.results_from_versions(filtered_versions, arguments)
        else:
            results = self.results_from_version(filtered_versions[0], arguments)
        return results

    def results(self, command: str) -> QueryResults:
        return self.results_from_arguments(self.parse_query_arguments(command))

    def reload(self):
        self.database.reload()
