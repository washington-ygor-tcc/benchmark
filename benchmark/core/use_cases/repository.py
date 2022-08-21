from benchmark.core.ports import MetricRepositoryPort, IdProviderPort
from benchmark.core.domain.prediction_request import PredictionRequest


def save(
    repository: MetricRepositoryPort,
    id_provider: IdProviderPort,
    requests: list[PredictionRequest],
) -> None:
    repository.save(id_provider.next_id(), requests)
