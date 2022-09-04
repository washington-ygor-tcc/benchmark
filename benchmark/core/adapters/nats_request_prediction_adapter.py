import asyncio
import json
import traceback
import nats

from contextlib import asynccontextmanager
from nats.aio.client import Client
from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.adapters.utils import json_default_serializer
from typing import Any, AsyncContextManager, Callable, Dict

from benchmark.core.ports.request_prediction_port import RequestPredictionPort
from benchmark.core.types import Id


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
            raise e
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
        self.subscription = None

    def __to_json(self, msg):
        return json.loads(msg.data)

    async def stop(self) -> None:
        if self.subscription is not None:
            try:
                await self.subscription.unsubscribe()
                self.subscription = None
                await asyncio.sleep(0)
            except nats.errors.ConnectionDrainingError:
                pass

    async def start(
        self,
        handle_callback: Callable[[Dict[str, Any]], None],
        on_started: Callable = None,
    ):
        connection: Client

        async def callback(msg):
            await handle_callback(self.__to_json(msg))

        async with self.__nats.connect() as connection:
            self.subscription = await connection.subscribe(self.__channel)
            on_started and on_started()
            async for msg in self.subscription.messages:
                await callback(msg)


class MessagingAdapter(RequestPredictionPort):
    def __init__(
        self, publisher: PublisherAdatper, subscriber: SubscriberAdapter
    ) -> None:
        self.__publisher = publisher
        self.__subscriber = subscriber
        self.__subscription_task = None
        self.__responses: Dict[Id, asyncio.Future] = {}

    async def get_prediction(
        self, request: PredictionRequest
    ) -> PredictionRequest:
        return await self.__publish(request)

    async def __handle(self, data: Dict[str, Any]):
        if (
            (request_id := data.get("request_id"))
            and request_id in self.__responses
            and not self.__responses[request_id].done()
        ):
            self.__responses[request_id].set_result(data)

    async def __start_subscription(self):
        is_subscription_ready = asyncio.get_event_loop().create_future()

        def set_is_subscription_ready():
            if not is_subscription_ready.done():
                is_subscription_ready.set_result(None)

        self.__subscription_task = asyncio.get_event_loop().create_task(
            self.__subscriber.start(
                self.__handle,
                set_is_subscription_ready,
            )
        )

        await is_subscription_ready

    async def __stop_subscription(self):
        if self.__subscription_task is not None and len(self.__responses) == 0:
            await self.__subscriber.stop()
            self.__subscription_task.cancel()
            self.__subscription_task = None

    def __add_future_response(self, request_id: Id):
        self.__responses[
            request_id
        ] = asyncio.get_running_loop().create_future()

    def __remove_future_response(self, request_id: Id):
        self.__responses.pop(request_id, None)

    async def __get_response(self, request_id: Id):
        return await self.__responses[request_id]

    async def __publish(self, prediction_request: PredictionRequest):
        self.__add_future_response(prediction_request.request_id)
        await self.__start_subscription()

        await self.__publisher.publish(prediction_request)
        response = await self.__get_response(prediction_request.request_id)

        self.__remove_future_response(prediction_request.request_id)
        await self.__stop_subscription()

        return response
