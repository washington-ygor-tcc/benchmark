import abc


class TimeProviderPort(abc.ABC):
    def time(self) -> float:
        pass
