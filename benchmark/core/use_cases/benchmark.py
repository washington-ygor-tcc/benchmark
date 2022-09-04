from __future__ import annotations
from contextlib import contextmanager
from time import monotonic, time
from typing import Dict
from uuid import uuid1

from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.ports import (
    IdProviderPort,
    RequestPredictionPort,
    TimeProviderPort,
)
from benchmark.core.types import (
    Id,
)

from benchmark.core.types import Features


def _next_id(id_provider: IdProviderPort = None) -> Id:
    if id_provider is not None:
        return id_provider.next_id()
    return uuid1()


def _get_time(timer_provider: TimeProviderPort = None):
    if timer_provider is not None:
        return timer_provider.time()
    return monotonic()


@contextmanager
def _setup_request(
    features: Features,
    id_provider: IdProviderPort = None,
    timer_provider: TimeProviderPort = None,
):
    try:
        request = PredictionRequest(
            _next_id(id_provider), features, _get_time(timer_provider)
        )
        yield request
    finally:
        request.end = _get_time(timer_provider)


async def run(
    features: Features,
    request_prediction: RequestPredictionPort,
    timer_provider: TimeProviderPort = None,
    id_provider: IdProviderPort = None,
):
    with _setup_request(features, id_provider, timer_provider) as request:
        request.prediction = await request_prediction.get_prediction(request)
        return request
