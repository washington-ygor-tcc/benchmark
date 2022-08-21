import abc


class MetricRepositoryPort(abc.ABC):
    def save(self, *args, **kwargs):
        pass
