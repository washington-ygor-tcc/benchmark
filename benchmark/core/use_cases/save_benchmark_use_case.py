from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.ports import (
    IdProviderPort,
    MetricRepositoryPort,
)


def save(
    repository: MetricRepositoryPort,
    requests: list[PredictionRequest],
    id_provider: IdProviderPort,
) -> None:
    repository.save(id_provider.next_id(), requests)
