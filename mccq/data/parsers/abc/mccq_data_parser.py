import abc


class MCCQDataParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, raw: dict): ...
