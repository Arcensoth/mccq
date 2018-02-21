import typing


class DataNode:
    def __init__(
            self,
            relevant: bool = None,
            population: int = None,
            key: str = None,
            command: str = None,
            command_t: str = None,
            argument: str = None,
            argument_t: str = None,
            collapsed: str = None,
            collapsed_t: str = None,
            children: typing.Dict[str, 'DataNode'] = None,
    ):
        self.relevant = relevant
        self.population = population
        self.key = key
        self.command = command
        self.command_t = command_t
        self.argument = argument
        self.argument_t = argument_t
        self.collapsed = collapsed
        self.collapsed_t = collapsed_t
        self.children = children or {}

    def leaves(self) -> typing.Iterable['DataNode']:
        # recursively yield nodes without children
        # depth-first
        if self.children:
            for child_key, child in self.children.items():
                yield from child.leaves()
        else:
            yield self
    #
    # @property
    # def relevant(self) -> bool:
    #     return self.executable or self.redirected or (self.executable and self.redirected and self.children)
    #
    # @property
    # def population(self) -> int:
    #     return sum(child.population for child in self.children.values()) + (1 if self.relevant else 0)
