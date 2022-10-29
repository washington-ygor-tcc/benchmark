import time

from benchmark.core.ports import TimeProviderPort

__all__ = ["TimeProviderAdapter"]


class TimeProviderAdapter(TimeProviderPort):
    def time(self, *args, **kwargs) -> float:
        return time.perf_counter()
