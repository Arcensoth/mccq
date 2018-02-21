import readline

from mccq.query_arguments import QueryArguments
from mccq.query_manager import QueryManager
from mccq.typedefs import IterableOfStrings


class CLICompleter:
    def __init__(self, query_manager: QueryManager):
        self.query_manager = query_manager
        self.completions = []

    def make_completions_for_version(self, version: str, arguments: QueryArguments) -> IterableOfStrings:
        # build a query tree as an intermediate result
        query_tree = self.query_manager.query_tree_for_version(version, arguments)

        # yield the key of the data node from each leaf of the query tree
        if query_tree:
            for leaf in query_tree.leaves():
                yield leaf.data_node.key

    def make_completions(self) -> IterableOfStrings:
        # this works similarly to actually querying a command, but instead of yielding all results we yield all leaf
        # nodes as suggestions for the next token

        try:
            # append wildcard to the end of the current command so we can invoke a mock query
            line = readline.get_line_buffer() + '.*'
            arguments = self.query_manager.parse_query_arguments(line)
            versions = self.query_manager.filter_versions(arguments)

        except:
            return None

        # spread across all versions applicable to the current command
        for v in versions:
            try:
                yield from self.make_completions_for_version(v, arguments)
            except:
                continue

    def complete(self, text: str, state: int):
        if state:
            return self.completions[state]
        else:
            # append completions with a space so that singular results are completed in full
            self.completions = tuple(word + ' ' for word in set(self.make_completions()))
            return self.completions[0]
