import typing


class DataNode:
    def __init__(
            self,
            population: int,
            argument: str = None,
            argument_t: str = None,
            command: str = None,
            command_t: str = None,
            collapsed: str = None,
            collapsed_t: str = None,
            relevant: bool = None,
            children: typing.Dict[str, 'DataNode'] = None,
    ):
        self.population = population
        self.command = command
        self.command_t = command_t
        self.argument = argument
        self.argument_t = argument_t
        self.collapsed = collapsed
        self.collapsed_t = collapsed_t
        self.relevant = relevant
        self.children = children
