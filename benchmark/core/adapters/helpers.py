import asyncio
import json
import nats

from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    AsyncContextManager,
)
from nats.aio.client import Client
from nats.aio.subscription import Subscription

from benchmark.core.domain import PredictionRequest
from benchmark.core.types import Id


@dataclass
class FutureResponses:
    responses: Dict[Id, asyncio.Future] = field(default_factory=dict)

    def set(self, response_id: Id):
        self.responses.update({response_id: self.loop.create_future()})

    def remove(self, response_id: Id):
        self.responses.pop(response_id, None)

    def get(self, response_id: Id):
        return self.responses.get(response_id)

    def has(self, response_id: Id):
        return response_id in self.responses

    def set_result(self, response_id: Id, result):
        if self.has(response_id) and not self.get(response_id).done():
            self.get(response_id).set_result(result)

    def is_empty(self) -> bool:
        return len(self.responses) == 0

    @property
    def loop(self):
        return asyncio.get_event_loop()


class NatsConnection:
    def __init__(self, nats_server_url: str) -> None:
        self.__nats_server_url = nats_server_url
        self.__conn = None
        self.__lock = asyncio.Lock()

    async def connect(self) -> Client:
        async with self.__lock:
            if self.__conn is None:
                self.__conn = await nats.connect(
                    self.__nats_server_url,
                )

            return self.__conn

    async def disconnect(self) -> None:
        async with self.__lock:
            if self.__conn is not None:
                await self.__conn.drain()
                self.__conn = None

    @asynccontextmanager
    async def connect_context(self) -> AsyncContextManager[Client]:
        try:
            yield await self.connect()
        finally:
            await self.disconnect()


class NatsPublisher:
    def __init__(self, nats_connection: NatsConnection, channel: str):
        self.__nats_conn = nats_connection
        self.__channel = channel

    async def publish(self, message: PredictionRequest) -> None:
        async with self.__nats_conn.connect_context() as conn:
            await conn.publish(
                self.__channel,
                json.dumps(message.todict()).encode("utf-8"),
            )


class NatsSubscriber:
    def __init__(self, nats_connection: NatsConnection, channel: str) -> None:
        self.__nats_conn = nats_connection
        self.__channel = channel
        self.__subscription_task = None
        self.__task_reference = set()
        self.__subscription: Subscription = None
        self.__lock = asyncio.Lock()

    async def start(
        self, handler: Callable[[Dict[str, Any]], Awaitable[None]]
    ):
        async with self.__lock:
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
            self.__task_reference.add(self.__subscription_task)
            self.__subscription_task.add_done_callback(
                self.__task_reference.discard
            )

        await is_subscription_ready

    async def stop(self, should_stop):
        async with self.__lock:
            if self.__subscription_task is not None and should_stop():
                await self.__subscription.unsubscribe()
                self.__subscription = None
                self.__subscription_task = None

    @asynccontextmanager
    async def start_context(
        self,
        handler: Callable[[Dict[str, Any]], Awaitable[None]],
        should_stop: Callable[[Any], bool],
    ):
        try:
            await self.start(handler)
            yield
        finally:
            await self.stop(should_stop)

    async def __start_subscription(
        self,
        handle_callback: Callable[[Dict[str, Any]], Awaitable[None]],
        set_is_ready: Callable = None,
    ):
        async with self.__nats_conn.connect_context() as conn:
            async with self.__lock:
                if self.__subscription is None:
                    self.__subscription = await conn.subscribe(self.__channel)

            set_is_ready()

            async for msg in self.__subscription.messages:
                await handle_callback(json.loads(msg.data))

    @property
    def loop(self):
        return asyncio.get_event_loop()
