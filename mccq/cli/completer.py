import typing

import readline

from mccq.cli.meta import META_COMMANDS
from mccq.query_arguments import QueryArguments
from mccq.query_manager import QueryManager
from mccq.typedefs import IterableOfStrings


class CLICompleter:
    def __init__(self, query_manager: QueryManager):
        self.query_manager = query_manager
        self.completions: typing.List[str] = []
        self.num_completions: int = 0
        self.reset_completions()

    def make_meta_completions(self, line: str) -> IterableOfStrings:
        command = line[1:]
        yield from ('\\' + s for s in META_COMMANDS if s.startswith(command))

    def make_query_completions_for_version(self, version: str, arguments: QueryArguments) -> IterableOfStrings:
        # build a query tree as an intermediate result
        query_tree = self.query_manager.query_tree_for_version(version, arguments)

        # yield the key of the data node from each leaf of the query tree
        if query_tree:
            for leaf in query_tree.leaves():
                yield leaf.data_node.key

    def make_query_completions(self, line: str) -> IterableOfStrings:
        # this works similarly to actually querying a command, but instead of yielding all results we yield all leaf
        # nodes as suggestions for the next token

        # append wildcard to the end of the current command so we can invoke a mock query
        command = line + '.*'

        try:
            arguments = self.query_manager.parse_query_arguments(command)
            versions = self.query_manager.filter_versions(arguments)

        except:
            return None

        # spread across all versions applicable to the current command
        for v in versions:
            try:
                yield from self.make_query_completions_for_version(v, arguments)
            except:
                continue

    def make_completions(self, line: str) -> IterableOfStrings:
        if line.startswith('\\'):
            yield from self.make_meta_completions(line)

        else:
            yield from self.make_query_completions(line)

    def reset_completions(self):
        self.completions = []
        self.num_completions = 0

    def complete(self, text: str, state: int):
        if state:
            if state == self.num_completions:
                self.reset_completions()
                return

            return self.completions[state]

        else:
            line = readline.get_line_buffer()

            # append completions with a space so that singular results are completed in full
            self.completions = tuple(word + ' ' for word in set(self.make_completions(line)))

            self.num_completions = len(self.completions)

            return self.completions[0]
