import asyncio

from time import time
from typing import Dict

from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.ports.metric_repository_port import MetricRepositoryPort
from benchmark.core.ports.id_provider_port import IdProviderPort
from benchmark.core.ports.request_prediction_port import RequestPredictionPort
from benchmark.core.ports.time_provider_port import TimeProviderPort
from benchmark.core.types import Features, Id


class Benchmark:
    def __init__(
        self,
        request_prediction: RequestPredictionPort,
        metric_repository: MetricRepositoryPort,
        timer_provider: TimeProviderPort = None,
        id_provider: IdProviderPort = None,
    ):
        self.__id_provider = id_provider
        self.__timer_provider = timer_provider
        self.__request_prediction = request_prediction
        self.__metric_repository = metric_repository
        self.__requests: Dict[Id, PredictionRequest] = dict()

    def set_requests(self, requests: list[Features]) -> None:
        for idx, request in enumerate(requests):
            request_id: Id = (
                self.__id_provider.next_id()
                if self.__id_provider is not None
                else idx
            )
            self.__set_request(
                PredictionRequest(request_id, request, None, None)
            )
        return self

    @property
    def requests(self) -> list[PredictionRequest]:
        return self.__requests.values()

    async def run(self) -> None:
        for request in self.requests:
            request.start = self.__get_time()
            response = await self.__request_prediction.get_prediction(request)
            if response is not None:
                request.end = self.__get_time()
            self.__set_request(request)

    def __set_request(self, request: PredictionRequest) -> None:
        self.__requests.update({request.id: request})

    def __get_time(self) -> float:
        if self.__timer_provider is None:
            return self.__timer_provider.time()
        return time()
