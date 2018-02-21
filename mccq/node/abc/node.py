import abc
import typing


class Node(abc.ABC):
    def leaves(self) -> typing.Iterable['Node']:
        if self.children:
            for child in self.children:
                yield from child.leaves()
        else:
            yield self

    @property
    @abc.abstractmethod
    def children(self) -> typing.Tuple['Node', ...]: ...
