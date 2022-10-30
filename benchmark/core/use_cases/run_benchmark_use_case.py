from contextlib import contextmanager

from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.ports import (
    IdProviderPort,
    RequestPredictionPort,
    TimeProviderPort,
)
from benchmark.core.types import Id, Features


@contextmanager
def __setup_request(
    features: Features,
    id_provider: IdProviderPort,
    time_provider: TimeProviderPort,
):
    try:
        request = PredictionRequest(id_provider.next_id(), features, time_provider.time())
        yield request
    finally:
        request.end = time_provider.time()


async def run(
    features: Features,
    request_prediction: RequestPredictionPort,
    timer_provider: TimeProviderPort,
    id_provider: IdProviderPort,
):
    with __setup_request(features, id_provider, timer_provider) as request:
        request.prediction = await request_prediction.get_prediction(request)
        return request
