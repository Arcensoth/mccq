import typing

from mccq.node.abc.node import Node


class DataNode(Node):
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
            children: typing.Tuple['DataNode', ...] = None,
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
        self._children = children

    def leaves(self) -> typing.Iterable['DataNode']:
        return super().leaves()

    @property
    def children(self) -> typing.Tuple['DataNode', ...]:
        return self._children or ()
