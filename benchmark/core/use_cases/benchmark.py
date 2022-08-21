from __future__ import annotations
from time import time
from typing import Dict

from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.ports import (
    IdProviderPort,
    RequestPredictionPort,
    TimeProviderPort,
)
from benchmark.core.types import (
    Id,
    ProgressIndicator,
    RequestGenerator,
)


class Benchmark:
    def __init__(
        self,
        request_prediction: RequestPredictionPort,
        timer_provider: TimeProviderPort = None,
        id_provider: IdProviderPort = None,
    ):
        self.__id_provider = id_provider
        self.__timer_provider = timer_provider
        self.__request_prediction = request_prediction
        self.__requests: Dict[Id, PredictionRequest] = dict()

    def set_requests(self, requests: RequestGenerator) -> Benchmark:
        for idx, request in enumerate(requests):
            request_id: Id = (
                self.__id_provider.next_id()
                if self.__id_provider is not None
                else idx
            )
            self.__set_request(PredictionRequest(request_id, request))
        return self

    @property
    def requests(self) -> list[PredictionRequest]:
        return self.__requests.values()

    async def run(self, progress_indicator: ProgressIndicator = None) -> None:
        requests = self.requests
        number_of_requests = len(requests)

        for idx, request in enumerate(requests):
            request.start = self.__get_time()
            response = await self.__request_prediction.get_prediction(request)
            if response is not None:
                request.end = self.__get_time()
                if progress_indicator is not None:
                    progress_indicator(idx, number_of_requests)
            self.__set_request(request)

    def __set_request(self, request: PredictionRequest) -> None:
        self.__requests.update({request.id: request})

    def __get_time(self) -> float:
        if self.__timer_provider is None:
            return self.__timer_provider.time()
        return time()
