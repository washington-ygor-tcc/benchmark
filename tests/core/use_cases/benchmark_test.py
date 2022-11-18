import asyncio
import time
import unittest

from unittest.mock import AsyncMock, Mock
from tests.utils import id_provider

from benchmark.core.use_cases import run_benchmark_use_case
from benchmark.core.ports import (
    RequestPredictionPort,
    MetricRepositoryPort,
    IdProviderPort,
    TimeProviderPort,
)

from benchmark.core.domain import PredictionRequest


class TestBenchmark(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.request_prediction = Mock(wraps=RequestPredictionPort)
        self.metric_repository = Mock(MetricRepositoryPort)
        self.id_provider = Mock(IdProviderPort)
        self.time_provider = Mock(TimeProviderPort())

        self.id_provider.next_id = Mock(side_effect=id_provider)
        self.time_provider.time = Mock(side_effect=time.monotonic)

    def __assert_request_result(self, result: PredictionRequest):
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.start)
        self.assertIsNotNone(result.end)
        self.assertIsNotNone(result.request_id)
        self.assertIsNotNone(result.features)
        self.assertIsNotNone(result.prediction)

    async def test_it_runs(self) -> None:
        self.request_prediction.get_prediction = AsyncMock(
            side_effect=lambda *args, **kwargs: {"status": "ok"}
        )

        result = await run_benchmark_use_case.run(
            {"id", 1},
            self.request_prediction,
            self.time_provider,
            self.id_provider,
        )

        self.__assert_request_result(result)
        self.assertEqual(result.prediction, {"status": "ok"})

    async def test_it_runs_for_multiple_requests(self) -> None:
        total_requests = 10
        self.request_prediction.get_prediction = AsyncMock(
            side_effect=lambda *args, **kwargs: {"status": "ok"}
        )

        results = await asyncio.gather(
            *[
                run_benchmark_use_case.run(
                    {"id", i},
                    self.request_prediction,
                    self.time_provider,
                    self.id_provider,
                )
                for i in range(total_requests)
            ]
        )

        self.assertEqual(len(results), total_requests)

        for result in results:
            self.__assert_request_result(result)
            self.assertEqual(result.prediction, {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
