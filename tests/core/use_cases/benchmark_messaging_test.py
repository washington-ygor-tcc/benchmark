import asyncio
import unittest


from unittest.mock import AsyncMock, Mock

from src.core.domain.prediction_request import PredictionRequest
from src.core.use_cases.benchmark_messaging import BenchmarkMessaging
from src.core.ports.client_message_port import MessagePublisherPort, MessageSubscriberPort
from src.core.ports.metric_repository_port import MetricRepositoryPort
from src.core.ports.id_provider_port import IdProviderPort

from .utils import id_provider


class TestBenchmarkMessaging(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.message_publisher = Mock(MessagePublisherPort)
        self.message_subscriber = Mock(MessageSubscriberPort)
        self.metric_repository = Mock(MetricRepositoryPort)
        self.id_provider = Mock(IdProviderPort)
        self.message_publisher.publish = AsyncMock(side_effect=lambda *args, **kwargs: None)

        self.benchmark_handle_call_count = 0

        def handle(handler, limit):
            for i in range(limit):
                handler({"id": i})
                self.benchmark_handle_call_count += i

        self.message_subscriber.handle = AsyncMock(side_effect=handle)

        self.id_provider.next_id = Mock(side_effect=id_provider())

        self.benchmark = BenchmarkMessaging(
            self.message_publisher, self.message_subscriber, self.metric_repository, self.id_provider
        )

    def _set_requests(self, total):
        self.benchmark.set_requests([{} for _ in range(total)])

    async def test_it_publishes_one(self):
        self.benchmark.set_requests([{}])

        await self.benchmark.run()

        self.assertEqual(self.message_publisher.publish.call_count, 1)

    async def test_it_publishes_multiple(self):
        total_requests = 10
        self._set_requests(total_requests)

        await self.benchmark.run()

        self.assertEqual(self.message_publisher.publish.call_count, total_requests)

    async def test_it_recieve_messages_from_subscription(self):
        total_requests = 10
        self._set_requests(total_requests)

        await self.benchmark.run()

        self.assertTrue(self.benchmark_handle_call_count, total_requests)

    async def test_it_returns_requests_with_timers_set(self):
        total_requests = 10
        self._set_requests(total_requests)

        await self.benchmark.run()

        for request in self.benchmark.requests():
            self.assertIsNotNone(request.start)
            self.assertIsNotNone(request.end)


if __name__ == "__main__":

    unittest.main()
