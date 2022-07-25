import time
import uuid
from typing import Dict

from src.core.domain.prediction_request import PredictionRequest
from src.core.ports.client_rest_api_port import ClientApiRestPort
from src.core.ports.metric_repository_port import MetricRepositoryPort


class BenchmarkAPI:
    def __init__(self, client_api: ClientApiRestPort, metric_repository: MetricRepositoryPort):
        self.__client_api = client_api
        self.__metric_repository = metric_repository
        self.__requests: Dict[uuid.UUID, PredictionRequest] = dict()

    def __set_request(self, request: PredictionRequest):
        self.__requests.update({request.id: request})

    def requests(self) -> list[PredictionRequest]:
        return self.__requests.values()

    def run(self, total_requests: int) -> None:
        for _ in range(total_requests):
            request = PredictionRequest(uuid.uuid4(), {}, time.time(), None)
            response = self.__client_api.get_prediction(request)
            if response:
                request.end = time.time()
            self.__set_request(request)
