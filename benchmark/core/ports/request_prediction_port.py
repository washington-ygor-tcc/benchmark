import abc
from typing import Dict, Any

from benchmark.core.domain.prediction_request import PredictionRequest

__all__ = ["RequestPredictionPort"]


class RequestPredictionPort(abc.ABC):
    @abc.abstractmethod
    async def get_prediction(
        request: PredictionRequest,
    ) -> Dict[str, Any] | None:
        pass
