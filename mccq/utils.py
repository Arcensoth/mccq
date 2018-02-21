import shlex

from mccq import errors
from mccq.argparser import ARGPARSER
from mccq.query_arguments import QueryArguments


def parse_query_arguments(command: str) -> QueryArguments:
    try:
        # split into tokens using shell-like syntax (preserve quoted substrings)
        parsed_args = ARGPARSER.parse_args(shlex.split(command))

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
