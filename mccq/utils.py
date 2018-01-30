import shlex

from mccq import errors
from mccq.argparser import ARGPARSER
from mccq.mccq_arguments import MCCQArguments


def parse_mccq_arguments(command: str) -> MCCQArguments:
    try:
        # split into tokens using shell-like syntax (preserve quoted substrings)
        parsed_args = ARGPARSER.parse_args(shlex.split(command))

        # return an object representation
        return MCCQArguments(
            command=tuple(parsed_args.command),  # immutable copy
            showtypes=parsed_args.showtypes,
            explode=parsed_args.explode,
            capacity=parsed_args.capacity,
            versions=tuple(parsed_args.version),  # duplicate versions are meaningless
        )

    except Exception as ex:
        raise errors.ArgumentParserFailedMCCQError(command) from ex
