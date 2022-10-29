import asyncio
import json
import nats


from contextlib import asynccontextmanager, contextmanager
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    AsyncIterator,
)
from nats.aio.client import Client
from nats.aio.subscription import Subscription

from benchmark.core.domain import PredictionRequest
from benchmark.core.adapters.utils import (
    json_default_serializer,
    FutureResponses,
)
from benchmark.core.ports import RequestPredictionPort
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
        self.__conn = None

    async def connect(self) -> Client:
        try:
            if (
                self.__conn is None
                or self.__conn.is_closed
                or not self.__conn.is_draining
            ):
                self.__conn = await nats.connect(
                    self.__nats_server_url,
                )
            return self.__conn
        except Exception as e:
            pass

    async def disconnect(self) -> None:
        try:
            if self.__conn is not None and not self.__conn.is_draining:
                await self.__conn.drain()
                self.__conn = None
        except Exception as e:
            pass

    @asynccontextmanager
    async def connect_conext(self) -> AsyncIterator[Client]:
        try:
            yield await self.connect()
            # await self.disconnect()
        except Exception as e:
            pass


class PublisherAdatper:
    def __init__(self, nats_connection: NatsConnection, channel: str):
        self.__nats_conn = nats_connection
        self.__channel = channel

    async def publish(self, message: PredictionRequest) -> None:
        async with self.__nats_conn.connect_conext() as conn:
            await conn.publish(
                self.__channel,
                json.dumps(
                    message.todict(), default=json_default_serializer
                ).encode("utf-8"),
            )


class SubscriberAdapter:
    def __init__(self, nats_connection: NatsConnection, channel: str) -> None:
        self.__nats_conn = nats_connection
        self.__channel = channel
        self.__subscription_task = None
        self.subscription: Subscription = None

    async def start(
        self, handler: Callable[[Dict[str, Any]], Awaitable[None]]
    ):
        is_subscription_ready = self.loop.create_future()
        self.__subscription_task = self.loop.create_task(
            self.__start_subscription(
                handler,
                lambda: (
                    not is_subscription_ready.done()
                    and is_subscription_ready.set_result(None)
                ),
            )
        )

        await is_subscription_ready

    async def stop(self, should_stop):
        if self.__subscription_task is not None and should_stop():
            await self.__stop_subscription()
            self.__subscription_task.cancel()
            self.__subscription_task = None

    @asynccontextmanager
    async def start_context(
        self,
        handler: Callable[[Dict[str, Any]], Awaitable[None]],
        should_stop: Callable[[Any], bool],
    ):
        await self.start(handler)
        yield
        await self.stop(should_stop)

    async def __start_subscription(
        self,
        handle_callback: Callable[[Dict[str, Any]], Awaitable[None]],
        set_is_ready: Callable = None,
    ):
        async with self.__nats_conn.connect_conext() as conn:
            if self.subscription is None:
                self.subscription = await conn.subscribe(self.__channel)

            set_is_ready()

            async for msg in self.subscription.messages:
                await handle_callback(json.loads(msg.data))

    async def __stop_subscription(self) -> None:
        if self.subscription is not None:
            try:
                await self.subscription.unsubscribe()
                self.subscription = None
                await asyncio.sleep(0)
            except Exception as e:
                raise e

    @property
    def loop(self):
        return asyncio.get_event_loop()


class MessagingAdapter(RequestPredictionPort):
    def __init__(
        self, publisher: PublisherAdatper, subscriber: SubscriberAdapter
    ) -> None:
        self.__publisher = publisher
        self.__subscriber = subscriber
        self.__responses = FutureResponses()

    async def get_prediction(
        self, request: PredictionRequest
    ) -> PredictionRequest:
        return await self.__publish(request)

    async def __publish(self, prediction_request: PredictionRequest):
        with self.__with_response(
            prediction_request.request_id
        ) as future_response:
            async with self.__subscriber.start_context(
                self.__handler, self.__responses.is_empty
            ):
                await self.__publisher.publish(prediction_request)
                response = await future_response
                return response.get("prediction")

    @contextmanager
    def __with_response(self, request_id: Id):
        self.__responses.set(request_id)
        yield self.__responses.get(request_id)
        self.__responses.remove(request_id)

    async def __handler(self, data: Dict[str, Any]):
        if request_id := data.get("request_id"):
            self.__responses.set_result(request_id, data)
