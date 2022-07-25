import abc
from typing import Any, Dict

from src.core.domain.prediction_request import PredictionRequest


class ClientApiRestPort(abc.ABC):
    @abc.abstractmethod
    def get_prediction(request: PredictionRequest) -> Dict[str, Any] | None:
        pass
