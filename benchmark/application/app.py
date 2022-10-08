import asyncio
import enum
import numpy as np
import yaml

from datetime import datetime
from typing import Dict, List, Tuple

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
from benchmark.core.types import (
    RequestGenerator,
)

from benchmark.core.ports import (
    IdProviderPort,
    RequestPredictionPort,
    TimeProviderPort,
)

from benchmark.core.domain.prediction_request import PredictionRequest


@enum.unique
class BenchmarkTypes(str, enum.Enum):
    API = "api"
    MESSAGING = "messaging"


__benchmark_adapters = Tuple[
    RequestPredictionPort, TimeProviderPort, IdProviderPort
]


def __get_config():
    with open("./benchmark/config.yaml", encoding="utf8") as file:
        config = yaml.safe_load(file)
        return config


def __get_timestamp():
    return datetime.now().strftime("%d_%m_%Y_%H_%M_%S")


def __get_benchmark_adapters(
    benchmark_type: BenchmarkTypes, config: Dict
) -> __benchmark_adapters:
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

        return messaging_adapter, time_provider, id_provider

    if benchmark_type == BenchmarkTypes.API:
        client_api = ClientApiRestRequestsAdapter(
            config["api"]["base_url"] + config["api"]["prediction"]
        )
        id_provider = UUIDProviderAdapter()
        time_provider = TimeProviderAdapter()

        return client_api, time_provider, id_provider


def run_benchmark(
    benchmark_type: BenchmarkTypes,
    request_generator: RequestGenerator,
) -> None:
    adapters = __get_benchmark_adapters(benchmark_type, __get_config())
    return asyncio.get_event_loop().run_until_complete(
        asyncio.gather(
            *[
                benchmark.run(features, *adapters)
                for features in request_generator
            ]
        )
    )


def save_benchmark_csv(
    benchmark_type: BenchmarkTypes, results=List[PredictionRequest]
):
    repository = MetricRepositoryAdapter(
        f"{benchmark_type}_{__get_timestamp()}.csv"
    )
    benchmark.save(repository, results)
