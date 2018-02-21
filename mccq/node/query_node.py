import typing

from mccq.node.abc.node import Node
from mccq.node.data_node import DataNode


class QueryNode(Node):
    def __init__(self, data_node: DataNode, children: typing.Tuple['QueryNode', ...] = None):
        self.data_node = data_node
        self._children = children

    def leaves(self) -> typing.Iterable['QueryNode']:
        return super().leaves()

    @property
    def children(self) -> typing.Tuple['QueryNode', ...]:
        return self._children or ()
