import abc

from mccq.typedefs import TupleOfStrings


class DataLoader(abc.ABC):
    @abc.abstractmethod
    def load(self, components: TupleOfStrings) -> dict: ...
