from __future__ import annotations

import aiohttp

from typing import Any, Dict
from benchmark.core.domain import PredictionRequest
from benchmark.core.ports import RequestPredictionPort
from benchmark.core.types import APIConfig


__all__ = ["ClientApiRestAiohttpAdapter"]


class ClientApiRestAiohttpAdapter(RequestPredictionPort):
    def __init__(self, url: str) -> None:
        self.__url = url

    @staticmethod
    def create(config: APIConfig) -> ClientApiRestAiohttpAdapter:
        return ClientApiRestAiohttpAdapter(
            "{}:{}{}".format(
                config.host,
                config.port,
                config.prediction_route,
            )
        )

    async def get_prediction(
        self, request: PredictionRequest
    ) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.__url, json=request.todict()
            ) as response:
                return await response.json()
