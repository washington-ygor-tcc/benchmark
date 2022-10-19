import os
import asyncio
import enum
import tqdm.auto

from typing import Dict, List, Tuple, Union

from benchmark.application import utils
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


def __get_benchmark_adapters(
    benchmark_type: BenchmarkTypes, config: Dict
) -> __benchmark_adapters:
    if benchmark_type == BenchmarkTypes.MESSAGING:
        nats_config = config["nats"]
        id_provider = UUIDProviderAdapter()
        time_provider = TimeProviderAdapter()
        nats_url = "{}:{}".format(nats_config["host"], nats_config["port"])

        messaging_adapter = MessagingAdapter(
            PublisherAdatper(
                NatsConnection(nats_url),
                nats_config["request_channel"],
            ),
            SubscriberAdapter(
                NatsConnection(nats_url),
                nats_config["response_channel"],
            ),
        )

        return messaging_adapter, time_provider, id_provider

    if benchmark_type == BenchmarkTypes.API:
        api_config = config["api"]
        client_api = ClientApiRestRequestsAdapter(
            "{}:{}{}".format(
                api_config["host"],
                api_config["port"],
                api_config["prediction"],
            )
        )
        id_provider = UUIDProviderAdapter()
        time_provider = TimeProviderAdapter()

        return client_api, time_provider, id_provider


def run_benchmark(
    benchmark_type: BenchmarkTypes,
    request_generator: RequestGenerator,
    config: Dict = {},
    show_progress_bar: bool = True,
) -> List[PredictionRequest]:
    config = utils.update_config(config, utils.get_default_config())
    adapters = __get_benchmark_adapters(benchmark_type, config)
    tasks = [
        benchmark.run(features, *adapters) for features in request_generator
    ]

    return asyncio.get_event_loop().run_until_complete(
        tqdm.auto.tqdm.gather(*tasks, disable=show_progress_bar)
    )


def save_benchmark_csv(
    benchmark_type: BenchmarkTypes,
    results=List[PredictionRequest],
    dest: Union[str, os.PathLike] = ".",
):
    if dest.endswith("/"):
        dest = dest[: -len(dest)]

    repository = MetricRepositoryAdapter(
        f"{dest}/{benchmark_type}_{utils.get_timestamp()}.csv"
    )
    benchmark.save(repository, results)
