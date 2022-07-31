import unittest

from unittest.mock import Mock
from .utils import id_provider

from src.core.use_cases.benchmark_api import BenchmarkAPI
from src.core.ports.client_rest_api_port import ClientApiRestPort
from src.core.ports.metric_repository_port import MetricRepositoryPort
from src.core.ports.id_provider_port import IdProviderPort


class TestBenchmarkAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client_api = Mock(wraps=ClientApiRestPort)
        self.metric_repository = Mock(MetricRepositoryPort)
        self.id_provider = Mock(IdProviderPort)
        self.benchmark = BenchmarkAPI(self.client_api, self.metric_repository, self.id_provider)

        self.id_provider.next_id = Mock(side_effect=id_provider())

    def _set_requests(self, total):
        self.benchmark.set_requests([{} for _ in range(total)])

    def test_it_run_for_one_request(self) -> None:
        self.client_api.get_prediction.return_value = {}
        self._set_requests(1)
        self.benchmark.run()
        self.assertEqual(len(self.benchmark.requests()), 1)

    def test_it_runs_for_multiple_requests(self) -> None:
        total_requests = 10
        self.client_api.get_prediction.return_value = {}
        self._set_requests(total_requests)
        self.benchmark.run()
        self.assertEqual(len(self.benchmark.requests()), 10)

    def test_it_returns_requests_with_timers_set(self) -> None:
        total_requests = 10
        self.client_api.get_prediction.return_value = {}
        self._set_requests(total_requests)
        self.benchmark.run()

        for request in self.benchmark.requests():
            self.assertIsNotNone(request.start)
            self.assertIsNotNone(request.end)


if __name__ == "__main__":
    unittest.main()
