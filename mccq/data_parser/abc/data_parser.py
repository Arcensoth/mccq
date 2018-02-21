import abc

from mccq.data_node import DataNode


class DataParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, raw: dict) -> DataNode: ...
