import asyncio

from time import time
from typing import Any, Dict

from src.core.domain.prediction_request import PredictionRequest
from src.core.ports.client_message_port import MessagePublisherPort, MessageSubscriberPort
from src.core.ports.metric_repository_port import MetricRepositoryPort
from src.core.ports.id_provider_port import IdProviderPort
from src.core.types import Features, Id


class BenchmarkMessaging:
    def __init__(
        self,
        publisher: MessagePublisherPort,
        subscriber: MessageSubscriberPort,
        metric_repository: MetricRepositoryPort,
        id_provider: IdProviderPort = None,
    ):
        self.__id_provider = id_provider
        self.__publisher = publisher
        self.__subscriber = subscriber
        self.__metric_repository = metric_repository
        self.__requests: Dict[Id, PredictionRequest] = dict()

    def set_requests(self, requests: list[Features]):
        for idx, request in enumerate(requests):
            request_id: Id = self.__id_provider.next_id() if self.__id_provider is not None else idx
            self.__set_request(PredictionRequest(request_id, request, None, None))

    def requests(self) -> list[PredictionRequest]:
        return self.__requests.values()

    async def run(self) -> None:
        await asyncio.gather(*map(self.__publish, self.requests()))
        await asyncio.create_task(self.__subscriber.handle(self.__handle, len(self.requests())))

    async def __publish(self, request: PredictionRequest):
        request.start = time()
        self.__set_request(request)
        await self.__publisher.publish(request)

    def __set_request(self, request: PredictionRequest):
        self.__requests.update({request.id: request})

    def __handle(self, data: Dict[str, Any]):
        if (request_id := data.get("id")) is None:
            return

        if (request := self.__requests.get(request_id)) is not None:
            request.end = time()
            self.__set_request(request)
