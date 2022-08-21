import asyncio
import enum
import numpy as np
import yaml

from benchmark.core.adapters.client_api_adapter import (
    ClientApiRestRequestsAdapter,
)
from benchmark.core.adapters.metric_repository_adapter import (
    MetricRepositoryAdapter,
)
from benchmark.core.adapters import (
    NatsConnection,
    PublisherAdatper,
    SubscriberAdapter,
    MessagingAdapter,
    UUIDProviderAdapter,
    TimeProviderAdapter,
)

from benchmark.core.use_cases.benchmark import Benchmark
from benchmark.core.use_cases import repository
from benchmark.core.types import (
    ProgressIndicator,
    RequestGenerator,
)


@enum.unique
class BenchmarkTypes(str, enum.Enum):
    API = "api"
    MESSAGING = "messaging"


def get_config():
    with open("./benchmark/config.yaml", encoding="utf8") as file:
        config = yaml.safe_load(file)
        return config


def create_benchmark(benchmark_type: BenchmarkTypes) -> Benchmark:
    config = get_config()

    if benchmark_type == BenchmarkTypes.MESSAGING:
        id_provider = UUIDProviderAdapter()
        time_provider = TimeProviderAdapter()
        messaging_adapter = MessagingAdapter(
            PublisherAdatper(
                NatsConnection(config["nats"]["url"]),
                config["nats"]["request_channel"],
            ),
            SubscriberAdapter(
                NatsConnection(config["nats"]["url"]),
                config["nats"]["response_channel"],
            ),
        )

        return Benchmark(messaging_adapter, time_provider, id_provider)

    if benchmark_type == BenchmarkTypes.API:
        client_api = ClientApiRestRequestsAdapter(
            config["api"]["base_url"] + config["api"]["prediction"]
        )
        id_provider = UUIDProviderAdapter()
        time_provider = TimeProviderAdapter()

        return Benchmark(client_api, time_provider, id_provider)


def run_benchmark(
    benchmark: Benchmark,
    request_generator: RequestGenerator,
    progress_indicator: ProgressIndicator = None,
) -> None:
    benchmark.set_requests(request_generator)
    asyncio.run(benchmark.run(progress_indicator))


def save_benchmark(benchmark: Benchmark):
    repository.save(
        MetricRepositoryAdapter, UUIDProviderAdapter(), benchmark.requests
    )


def calculate_avarage(benchmark: Benchmark) -> object:
    data = np.array(
        [request.end - request.start for request in benchmark.requests]
    )
    return f"média {data.mean()} {data.max()} {data.min()}"
