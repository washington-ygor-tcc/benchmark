import asyncio
import uuid
from time import time
from typing import Any, Dict

from src.core.domain.prediction_request import PredictionRequest
from src.core.ports.client_message_port import MessagePublisherPort, MessageSubscriberPort
from src.core.ports.metric_repository_port import MetricRepositoryPort


class BenchmarkMessaging:
    def __init__(
        self,
        publisher: MessagePublisherPort,
        subscriber: MessageSubscriberPort,
        metric_repository: MetricRepositoryPort,
    ):
        self.__publisher = publisher
        self.__subscriber = subscriber
        self.__metric_repository = metric_repository
        self.__requests: Dict[uuid.UUID, PredictionRequest] = dict()

    def __set_request(self, request: PredictionRequest):
        self.__requests.update({request.id: request})

    def requests(self) -> list[PredictionRequest]:
        return self.__requests.values()

    def __handle(self, data: Dict[str, Any]):
        request = self.__requests.get(uuid.UUID(data.get("id")))
        request.end = time()
        self.__set_request(request)

    async def run(self, total_requests: int) -> None:
        task = asyncio.create_task(self.__subscriber.handle(self.__handle, total_requests))

        async def make_request():
            request = PredictionRequest(uuid.uuid4(), {"hello": "world"}, time(), None)
            self.__set_request(request)
            await self.__publisher.publish(request)

        await asyncio.gather(*[make_request() for _ in range(total_requests)])
        await task
