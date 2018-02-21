from mccq.typedefs import TupleOfStrings


class QueryArguments:
    def __init__(
            self,
            command: TupleOfStrings,
            showtypes: bool = None,
            explode: bool = None,
            capacity: int = None,
            versions: TupleOfStrings = None,
    ):
        self.command = command
        self.showtypes = showtypes
        self.explode = explode
        self.capacity = capacity
        self.versions = versions
