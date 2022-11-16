from __future__ import annotations
from contextlib import contextmanager
from typing import (
    Any,
    Dict,
)

from benchmark.core.domain import PredictionRequest
from benchmark.core.adapters.helpers import (
    FutureResponses,
    NatsPublisher,
    NatsSubscriber,
    NatsConnection,
)

from benchmark.core.ports import RequestPredictionPort
from benchmark.core.types import Id


__all__ = [
    "NatsMessagingAdapter",
]


class NatsMessagingAdapter(RequestPredictionPort):
    def __init__(self, publisher: NatsPublisher, subscriber: NatsSubscriber) -> None:
        self.__publisher = publisher
        self.__subscriber = subscriber
        self.__responses = FutureResponses()

    @staticmethod
    def create(
        nats_server: str,
        prediction_request_channel: str,
        prediction_response_channel: str,
    ) -> NatsMessagingAdapter:

        return NatsMessagingAdapter(
            NatsPublisher(NatsConnection(nats_server), prediction_request_channel),
            NatsSubscriber(NatsConnection(nats_server), prediction_response_channel),
        )

    async def get_prediction(self, request: PredictionRequest) -> PredictionRequest:
        return await self.__publish(request)

    async def __publish(self, prediction_request: PredictionRequest):
        async with self.__subscriber.start_context(
            self.__handler, self.__responses.is_empty
        ):
            with self.__with_response(prediction_request.request_id) as future_response:
                await self.__publisher.publish(prediction_request)
                response = await future_response
                return response.get("prediction")

    @contextmanager
    def __with_response(self, request_id: Id):
        try:
            self.__responses.set(request_id)
            yield self.__responses.get(request_id)
        finally:
            self.__responses.remove(request_id)

    async def __handler(self, data: Dict[str, Any]):
        if request_id := data.get("request_id"):
            self.__responses.set_result(request_id, data)
