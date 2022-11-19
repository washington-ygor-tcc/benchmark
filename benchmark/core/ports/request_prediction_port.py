from typing import Dict, Any

from benchmark.core.domain.prediction_request import PredictionRequest

__all__ = ["RequestPredictionPort"]


class RequestPredictionPort:
    async def get_prediction(
        self,
        request: PredictionRequest,
    ) -> Dict[str, Any] | None:
        raise NotImplementedError
