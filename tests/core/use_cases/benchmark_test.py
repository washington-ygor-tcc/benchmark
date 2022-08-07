import time
import unittest

from unittest.mock import AsyncMock, Mock
from .utils import id_provider

from src.core.use_cases.benchmark import Benchmark
from src.core.ports.request_prediction_port import RequestPredictionPort
from src.core.ports.metric_repository_port import MetricRepositoryPort
from src.core.ports.id_provider_port import IdProviderPort
from src.core.ports.time_provider_port import TimeProviderPort


class TestBenchmarkAPI(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.request_prediction = Mock(wraps=RequestPredictionPort)
        self.metric_repository = Mock(MetricRepositoryPort)
        self.id_provider = Mock(IdProviderPort)
        self.time_provider = Mock(TimeProviderPort())

        self.benchmark = Benchmark(
            self.request_prediction,
            self.metric_repository,
            self.time_provider,
            self.id_provider,
        )

        self.id_provider.next_id = Mock(side_effect=id_provider())
        self.time_provider.time = Mock(side_effect=time.time())

    def _set_requests(self, total):
        self.benchmark.set_requests([{} for _ in range(total)])

    async def test_it_run_for_one_request(self) -> None:
        self.request_prediction.get_prediction = AsyncMock(
            side_effect=lambda *args, **kwargs: {}
        )
        self._set_requests(1)
        await self.benchmark.run()
        self.assertEqual(len(self.benchmark.requests), 1)

    async def test_it_runs_for_multiple_requests(self) -> None:
        total_requests = 10
        self.request_prediction.get_prediction = AsyncMock(
            side_effect=lambda *args, **kwargs: {}
        )
        self._set_requests(total_requests)
        await self.benchmark.run()
        self.assertEqual(len(self.benchmark.requests), 10)

    async def test_it_returns_requests_with_timers_set(self) -> None:
        total_requests = 10
        self.request_prediction.get_prediction = AsyncMock(
            side_effect=lambda *args, **kwargs: {}
        )
        self._set_requests(total_requests)
        await self.benchmark.run()

        for request in self.benchmark.requests:
            self.assertIsNotNone(request.start)
            self.assertIsNotNone(request.end)


if __name__ == "__main__":
    unittest.main()
