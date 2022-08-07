import asyncio
import enum

import numpy as np

from benchmark.core.adapters.client_api_adapter import (
    ClientApiRestRequestsAdapter,
)
from benchmark.core.adapters.metric_repository_adapter import MetricRepository
from benchmark.core.adapters.nats_request_prediction_adapter import (
    NatsConnection,
    PublisherAdatper,
    SubscriberAdapter,
    MessagingAdapter,
)
from benchmark.core.adapters.uuid_provider_adapter import UUIDProviderAdapter
from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.use_cases.benchmark import Benchmark
from yaml import load, loader


def calculate_avarage(requests: list[PredictionRequest]):
    data = np.array([request.end - request.start for request in requests])
    print(f"média {data.mean()} {data.max()} {data.min()}")


async def main():
    with open("./src/config.yaml", encoding="utf8") as file:
        config = load(file, Loader=loader.SafeLoader)
        nats_connection_1 = NatsConnection(config["nats"]["url"])
        nats_connection_2 = NatsConnection(config["nats"]["url"])
        publisher = PublisherAdatper(
            nats_connection_1, config["nats"]["request_channel"]
        )
        subscriber = SubscriberAdapter(
            nats_connection_2, config["nats"]["response_channel"]
        )

        metric_repository = MetricRepository()
        id_provider = UUIDProviderAdapter()
        messaging_adapter = MessagingAdapter(publisher, subscriber)

        async with messaging_adapter.start_subscription():
            benchmark = Benchmark(
                messaging_adapter, metric_repository, id_provider
            )
            benchmark.set_requests([{} for _ in range(10)])
            await benchmark.run()
            print(calculate_avarage(benchmark.requests))

        client_api = ClientApiRestRequestsAdapter(
            config["api"]["base_url"] + config["api"]["prediction"]
        )
        benchmark_api = Benchmark(client_api, metric_repository, id_provider)
        benchmark_api.set_requests([{} for _ in range(10)])
        await benchmark_api.run()
        print(calculate_avarage(benchmark_api.requests))


if __name__ == "__main__":
    asyncio.run(main())
