import time

from benchmark.core.ports.time_provider_port import TimeProviderPort


class TimeProviderAdapter(TimeProviderPort):
    def time(self, *args, **kwargs) -> float:
        return time.monotonic()
