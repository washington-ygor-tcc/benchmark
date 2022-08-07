import abc


class IdProviderPort(abc.ABC):
    @abc.abstractmethod
    def next_id(self) -> int | str:
        pass
