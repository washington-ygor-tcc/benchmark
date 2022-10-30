import json
import aiohttp

from typing import Any, Dict
from benchmark.core.domain import PredictionRequest
from benchmark.core.ports import RequestPredictionPort

__all__ = ["ClientApiRestAiohttpAdapter"]


class ClientApiRestAiohttpAdapter(RequestPredictionPort):
    def __init__(self, url: str) -> None:
        self.__url = url

    async def get_prediction(self, request: PredictionRequest) -> Dict[int, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.__url, json=request.todict()) as response:
                return await response.json()
