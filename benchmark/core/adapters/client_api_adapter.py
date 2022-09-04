import asyncio
import requests
import json


from typing import Any, Dict
from benchmark.core.adapters.utils import json_default_serializer
from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.ports.request_prediction_port import RequestPredictionPort


class ClientApiRestRequestsAdapter(RequestPredictionPort):
    def __init__(self, url: str) -> None:
        self.__url = url

    def __get_prediction(self, request: PredictionRequest) -> Dict[str, Any]:

        prediction_response = requests.post(
            self.__url,
            json.dumps(request.todict(), default=json_default_serializer),
        )

        prediction = json.loads(prediction_response.text)
        return prediction

    async def get_prediction(
        self, request: PredictionRequest
    ) -> Dict[int, Any]:
        return await asyncio.coroutine(self.__get_prediction)(request)
