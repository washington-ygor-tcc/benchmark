import asyncio
import json
import nats

from contextlib import asynccontextmanager
from nats.aio.client import Client
from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.adapters.utils import json_default_serializer
from typing import Any, AsyncContextManager, Callable, Dict

from benchmark.core.ports.request_prediction_port import RequestPredictionPort


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
            await self.__subscription.unsubscribe()

    async def start(self, handle_callback: Callable[[Dict[str, Any]], None]):
        connection: Client

        async def callback(msg):
            await handle_callback(self.__to_json(msg))

        async with self.__nats.connect() as connection:

            self.__subscription = await connection.subscribe(self.__channel)
            async for msg in self.__subscription.messages:
                await callback(msg)


class MessagingAdapter(RequestPredictionPort):
    def __init__(
        self, publisher: PublisherAdatper, subscriber: SubscriberAdapter
    ) -> None:
        self.__publisher = publisher
        self.__subscriber = subscriber
        self.__subscription_task = None
        self.__responses = {}

    async def get_prediction(
        self, prediction: PredictionRequest
    ) -> PredictionRequest:
        async with self.__subscription_ctx():
            prediction = await self.__publish(prediction)

        return prediction

    async def __handle(self, data: Dict[str, Any]):
        if (request_id := data.get("id")) is not None:
            self.__responses[request_id].set_result(data)

    @asynccontextmanager
    async def __subscription_ctx(self):
        try:
            await self.__start_subscription()
            yield
        finally:
            await self.__stop_subscription()

    async def __start_subscription(self):
        self.__subscription_task = asyncio.create_task(
            self.__subscriber.start(self.__handle)
        )

    async def __stop_subscription(self):
        if self.__subscription_task is not None:
            await self.__subscriber.stop()
            self.__subscription_task.cancel()

    async def __wait_for_response(self, request_id: int):
        def remove_response_on_done(future: asyncio.Future):
            self.__responses.pop(request_id, None)

        future_response = asyncio.get_running_loop().create_future()
        future_response.add_done_callback(remove_response_on_done)

        self.__responses[request_id] = future_response

        return await future_response

    async def __publish(self, prediction: PredictionRequest):
        await self.__publisher.publish(prediction)
        return await self.__wait_for_response(prediction.id)
