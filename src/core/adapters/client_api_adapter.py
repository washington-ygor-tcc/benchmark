import json
from typing import Any, Dict

import requests
from src.core.adapters.nats_adapter import default
from src.core.domain.prediction_request import PredictionRequest
from src.core.ports.client_rest_api_port import ClientApiRestPort


class ClientApiRestRequestsAdapter(ClientApiRestPort):
    def __init__(self, url: str) -> None:
        self.__url = url

    def get_prediction(self, request: PredictionRequest) -> Dict[str, Any]:
        prediction_response = requests.post(
            self.__url,
            json.dumps(request.todict(), default=default)
        )
        prediction = json.loads(prediction_response.text)
        return prediction
