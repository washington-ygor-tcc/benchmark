from __future__ import annotations
from contextlib import contextmanager
from time import monotonic
from uuid import uuid1

from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.ports import (
    IdProviderPort,
    RequestPredictionPort,
    TimeProviderPort,
    MetricRepositoryPort,
)

from benchmark.core.types import Id, Features


def __next_id(id_provider: IdProviderPort = None) -> Id:
    if id_provider is not None:
        return id_provider.next_id()
    return uuid1()


def __get_time(time_provider: TimeProviderPort = None):
    if time_provider is not None:
        return time_provider.time()
    return monotonic()


@contextmanager
def _setup_request(
    features: Features,
    id_provider: IdProviderPort = None,
    time_provider: TimeProviderPort = None,
):
    try:
        request = PredictionRequest(
            __next_id(id_provider), features, __get_time(time_provider)
        )
        yield request
    finally:
        request.end = __get_time(time_provider)


async def run(
    features: Features,
    request_prediction: RequestPredictionPort,
    timer_provider: TimeProviderPort = None,
    id_provider: IdProviderPort = None,
):
    with _setup_request(features, id_provider, timer_provider) as request:
        request.prediction = await request_prediction.get_prediction(request)
        return request


def save(
    repository: MetricRepositoryPort,
    requests: list[PredictionRequest],
    id_provider: IdProviderPort = None,
) -> None:
    repository.save(__next_id(id_provider), requests)
