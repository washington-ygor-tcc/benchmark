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
from benchmark.core.use_cases.benchmark import Benchmark
from yaml import load, loader


@enum.unique
class BenchmarkTypes(str, enum.Enum):
    API = "api"
    MESSAGING = "messaging"


async def create_benchmark(
    benchmark_type: BenchmarkTypes, total_requests: int
) -> Benchmark:
    with open("./benchmark/config.yaml", encoding="utf8") as file:
        config = load(file, Loader=loader.SafeLoader)

        if benchmark_type == BenchmarkTypes.MESSAGING:
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

            benchmark = Benchmark(
                messaging_adapter, metric_repository, id_provider
            )

            benchmark = Benchmark(
                messaging_adapter, metric_repository, id_provider
            )
            benchmark.set_requests([{} for _ in range(total_requests)])
            await benchmark.run()

            return benchmark

        if benchmark_type == BenchmarkTypes.API:
            client_api = ClientApiRestRequestsAdapter(
                config["api"]["base_url"] + config["api"]["prediction"]
            )
            metric_repository = MetricRepository()
            id_provider = UUIDProviderAdapter()

            benchmark = Benchmark(client_api, metric_repository, id_provider)
            benchmark.set_requests([{} for _ in range(total_requests)])
            await benchmark.run()

            return benchmark


def calculate_avarage(benchmark: Benchmark):
    data = np.array(
        [request.end - request.start for request in benchmark.requests]
    )
    return f"média {data.mean()} {data.max()} {data.min()}"
