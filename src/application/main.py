import asyncio

import numpy as np

from src.core.adapters.client_api_adapter import ClientApiRestRequestsAdapter
from src.core.adapters.metric_repository_adapter import MetricRepository
from src.core.adapters.nats_adapter import NatsConnection, PublisherAdatper, SubscriberAdapter
from src.core.adapters.uuid_provider_adapter import UUIDProviderAdapter
from src.core.domain.prediction_request import PredictionRequest
from src.core.use_cases.benchmark_api import BenchmarkAPI
from src.core.use_cases.benchmark_messaging import BenchmarkMessaging
from yaml import load, loader


def calculate_avarage(requests: list[PredictionRequest]):
    data = np.array([request.end - request.start for request in requests])
    print(f"média {data.mean()} {data.max()} {data.min()}")


async def main():
    with open("./src/config.yaml", encoding="utf8") as file:
        config = load(file, Loader=loader.SafeLoader)
        nats_connection_1 = NatsConnection(config["nats"]["url"])
        nats_connection_2 = NatsConnection(config["nats"]["url"])
        pulisher = PublisherAdatper(nats_connection_1, config["nats"]["request_channel"])
        subscriber = SubscriberAdapter(nats_connection_2, config["nats"]["response_channel"])

        metric_repository = MetricRepository()
        id_provider = UUIDProviderAdapter()

        benchmark_messaging = BenchmarkMessaging(pulisher, subscriber, metric_repository, id_provider)
        benchmark_messaging.set_requests([{} for _ in range(10)])
        await benchmark_messaging.run()
        print(calculate_avarage(benchmark_messaging.requests()))

        client_api = ClientApiRestRequestsAdapter(config["api"]["base_url"] + config["api"]["prediction"])
        benchmark_api = BenchmarkAPI(client_api, metric_repository, id_provider)
        benchmark_api.set_requests([{} for _ in range(10)])
        benchmark_api.run()
        print(calculate_avarage(benchmark_api.requests()))


if __name__ == "__main__":
    asyncio.run(main())
