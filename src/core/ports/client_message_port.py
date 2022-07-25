import abc
from typing import Callable

from src.core.domain.prediction_request import PredictionRequest


class MessagePublisherPort(abc.ABC):
    @abc.abstractmethod
    def publish(self, message: PredictionRequest):
        pass


class MessageSubscriberPort(abc.ABC):
    @abc.abstractmethod
    def handle(self, handle_callback: Callable, limit: int):
        pass
