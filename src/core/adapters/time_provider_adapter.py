import time

from src.core.ports.time_provider_port import TimerProviderPort


class TimeProviderAdapter(TimerProviderPort):
    def time(self, *args, **kwargs) -> float:
        return time.monotonic()
