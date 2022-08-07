import asyncio
import json
import nats

from contextlib import asynccontextmanager
from nats.aio.client import Client
from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.adapters.utils import json_default_serializer
from typing import Any, AsyncContextManager, Callable, Dict


__all__ = [
    "NatsConnection",
    "PublisherAdatper",
    "SubscriberAdapter",
    "MessagingAdapter",
]


class NatsConnection:
    def __init__(self, nats_server_url: str) -> None:
        self.__nats_server_url = nats_server_url

    @asynccontextmanager
    async def connect(self) -> AsyncContextManager[Client]:
        nats_connection = None
        try:
            nats_connection = await nats.connect(self.__nats_server_url)
            yield nats_connection
        except Exception as e:
            print(e)
        finally:
            if nats_connection:
                await nats_connection.drain()


class PublisherAdatper:
    def __init__(self, nats_connection: NatsConnection, channel: str):
        self.__nats = nats_connection
        self.__channel = channel

    async def publish(self, message: PredictionRequest) -> None:
        connection: Client
        async with self.__nats.connect() as connection:
            await connection.publish(
                self.__channel,
                json.dumps(
                    message.todict(), default=json_default_serializer
                ).encode("utf-8"),
            )


class SubscriberAdapter:
    def __init__(self, nats_connection: NatsConnection, channel: str) -> None:
        self.__nats = nats_connection
        self.__channel = channel
        self.__subscription = None

    def __to_json(self, msg):
        return json.loads(msg.data)

    async def stop(self) -> None:
        if self.__subscription is not None:
            await self.__subscription.drain()

    async def start(self, handle_callback: Callable[[Dict[str, Any]], None]):
        connection: Client
        async with self.__nats.connect() as connection:
            self.__subscription = await connection.subscribe(self.__channel)
            try:
                async for msg in self.__subscription.messages:
                    handle_callback(self.__to_json(msg))
            except Exception as e:
                print("aaaa", e)


class MessagingAdapter:
    def __init__(
        self, publisher: PublisherAdatper, subscriber: SubscriberAdapter
    ) -> None:
        self.__publisher = publisher
        self.__subscriber = subscriber
        self.__subscription_task = None
        self.__queue = asyncio.Queue()

    def __handle(self, data: Dict[str, Any]):
        if data.get("id") is not None:
            self.__queue.put_nowait(data)

    @asynccontextmanager
    async def start_subscription(self):
        try:
            self.__subscription_task = asyncio.create_task(
                self.__subscriber.start(self.__handle)
            )
            yield
        finally:
            await self.stop_subscription()

    async def stop_subscription(self):
        if self.__subscription_task is not None:
            await self.__subscriber.stop()
            self.__subscription_task.cancel()

    async def __publish(self, prediction: PredictionRequest):
        await self.__publisher.publish(prediction)

        async def wait_for_response():
            while (response := await self.__queue.get()) and response.get(
                "id"
            ) != prediction.id:
                self.__queue.put_nowait(response)

            return response

        return await asyncio.create_task(wait_for_response())

    async def get_prediction(
        self, prediction: PredictionRequest
    ) -> PredictionRequest:
        return await self.__publish(prediction)
