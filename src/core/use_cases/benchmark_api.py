import time

from typing import Dict

from src.core.domain.prediction_request import PredictionRequest
from src.core.ports.client_rest_api_port import ClientApiRestPort
from src.core.ports.metric_repository_port import MetricRepositoryPort
from src.core.ports.id_provider_port import IdProviderPort
from src.core.types import Features, Id


class BenchmarkAPI:
    def __init__(
        self,
        client_api: ClientApiRestPort,
        metric_repository: MetricRepositoryPort,
        id_provider: IdProviderPort,
    ):
        self.__client_api = client_api
        self.__metric_repository = metric_repository
        self.__id_provider = id_provider
        self.__requests: Dict[Id, PredictionRequest] = dict()

    def set_requests(self, requests: list[Features]):
        for idx, request in enumerate(requests):
            request_id: Id = self.__id_provider.next_id() if self.__id_provider is not None else idx
            self.__set_request(PredictionRequest(request_id, request, None, None))

    def __set_request(self, request: PredictionRequest):
        self.__requests.update({request.id: request})

    def requests(self) -> list[PredictionRequest]:
        return self.__requests.values()

    def run(self) -> None:
        for request in self.requests():
            request.start = time.time()
            response = self.__client_api.get_prediction(request)
            if response is not None:
                request.end = time.time()
            self.__set_request(request)
