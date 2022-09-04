import asyncio
import enum
from typing import Dict
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

from benchmark.core.use_cases import benchmark
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


async def _run_messaging_benchmark(
    config: Dict,
    request_generator: RequestGenerator,
):
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

    return await asyncio.gather(
        *[
            benchmark.run(
                features, messaging_adapter, time_provider, id_provider
            )
            for features in request_generator
        ]
    )


async def _run_api_benchmark(
    config: Dict,
    request_generator: RequestGenerator,
):
    client_api = ClientApiRestRequestsAdapter(
        config["api"]["base_url"] + config["api"]["prediction"]
    )
    id_provider = UUIDProviderAdapter()
    time_provider = TimeProviderAdapter()

    return await asyncio.gather(
        *[
            benchmark.run(features, client_api, time_provider, id_provider)
            for features in request_generator
        ]
    )


def run_benchmark(
    benchmark_type: BenchmarkTypes,
    request_generator: RequestGenerator,
) -> None:
    if benchmark_type == BenchmarkTypes.MESSAGING:
        return asyncio.get_event_loop().run_until_complete(
            _run_messaging_benchmark(get_config(), request_generator)
        )
    if benchmark_type == BenchmarkTypes.API:
        return asyncio.get_event_loop().run_until_complete(
            _run_api_benchmark(get_config(), request_generator)
        )
