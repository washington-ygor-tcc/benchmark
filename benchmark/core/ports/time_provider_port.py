__all__ = ["TimeProviderPort"]


class TimeProviderPort:
    def time(self) -> float:
        raise NotImplementedError
