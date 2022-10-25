import abc

__all__ = ["IdProviderPort"]


class IdProviderPort(abc.ABC):
    @abc.abstractmethod
    def next_id(self) -> int | str:
        pass
