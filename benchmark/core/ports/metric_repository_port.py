import abc

__all__ = ["MetricRepositoryPort"]


class MetricRepositoryPort(abc.ABC):
    def save(self, *args, **kwargs):
        pass
