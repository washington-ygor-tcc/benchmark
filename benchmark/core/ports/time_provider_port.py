import abc

__all__ = ["TimeProviderPort"]


class TimeProviderPort(abc.ABC):
    def time(self) -> float:
        pass
