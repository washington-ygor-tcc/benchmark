import datetime
import json
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncContextManager, Callable, Dict

import nats
from nats.aio.client import Client
from nats.aio.subscription import Subscription
from src.core.domain.prediction_request import PredictionRequest
from src.core.ports.client_message_port import MessagePublisherPort, MessageSubscriberPort

from src.core.adapters.utils import default


class NatsConnection:
    def __init__(self, nats_server_url: str) -> None:
        self.__nats_server_url = nats_server_url

    @asynccontextmanager
    async def connect(self) -> AsyncContextManager[Client]:
        try:
            nats_connection = await nats.connect(self.__nats_server_url)
            yield nats_connection
        finally:
            await nats_connection.drain()


class PublisherAdatper(MessagePublisherPort):
    def __init__(self, nats_connection: NatsConnection, channel: str):
        self.__nats = nats_connection
        self.__channel = channel

    async def publish(self, message: PredictionRequest) -> None:
        connection: Client
        async with self.__nats.connect() as connection:
            await connection.publish(
                self.__channel,
                json.dumps(message.todict(), default=default).encode("utf-8"),
            )


class SubscriberAdapter(MessageSubscriberPort):
    def __init__(self, nats_connection: NatsConnection, channel: str) -> None:
        self.__nats = nats_connection
        self.__channel = channel

    def __to_json(self, msg):
        return json.loads(msg.data)

    async def handle(
        self,
        handle_callback: Callable[[Dict[str, Any]], None],
        limit: int,
    ):
        connection: Client

        async with self.__nats.connect() as connection:
            subscription = await connection.subscribe(self.__channel)
            await subscription.unsubscribe(limit=limit)
            try:
                async for msg in subscription.messages:
                    handle_callback(self.__to_json(msg))
            except Exception as e:
                print(e)
