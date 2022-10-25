import enum
import os
import pkg_resources
import yaml
import collections.abc
import tabulate
import statistics

from datetime import datetime
from typing import Dict, Union, Tuple, List

from benchmark.core.adapters import (
    NatsConnection,
    PublisherAdatper,
    SubscriberAdapter,
    MessagingAdapter,
    UUIDProviderAdapter,
    TimeProviderAdapter,
    ClientApiRestRequestsAdapter,
)

from benchmark.core.ports import (
    IdProviderPort,
    RequestPredictionPort,
    TimeProviderPort,
)

from benchmark.core.domain.prediction_request import PredictionRequest


__benchmark_adapters = Tuple[
    RequestPredictionPort, TimeProviderPort, IdProviderPort
]


@enum.unique
class BenchmarkTypes(str, enum.Enum):
    API = "api"
    MESSAGING = "messaging"


def update_config(update: Dict, config: Dict) -> Dict:
    for key, value in update.items():
        if isinstance(value, collections.abc.Mapping):
            config[key] = update_config(value, config.get(key, {}))
        else:
            config[key] = value
    return config


def get_default_config(path: Union[str, os.PathLike] = "../config.yaml"):
    return yaml.safe_load(pkg_resources.resource_string(__name__, path))


def get_timestamp():
    return datetime.now().strftime("%d_%m_%Y_%H_%M_%S")


def get_benchmark_adapters(
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


def string_table_result(results: List[PredictionRequest]):
    if not all([result.prediction for result in results]):
        print("Not OK")

    def as_date(ts):
        return datetime.fromtimestamp(ts).strftime(".%f")

    return tabulate.tabulate(
        [
            [
                result.request_id,
                as_date(result.start),
                as_date(result.end),
                result.prediction,
            ]
            for result in results
        ],
        headers=["Id", "Start", "End", "Data"],
        floatfmt=".20f",
    )


def stats(results: List[PredictionRequest]):
    times = list(map(lambda r: r.end - r.start, results))
    first_request = min(map(lambda r: r.start, results))
    last_request = max(map(lambda r: r.end, results))
    total_time = last_request - first_request

    return tabulate.tabulate(
        [
            [
                len(results),
                total_time,
                min(times),
                max(times),
                statistics.mean(times),
                statistics.stdev(times),
                len(results) / total_time,
            ]
        ],
        headers=[
            "Nº Requests",
            "Total time",
            "Min",
            "Max",
            "Mean",
            "STD",
            "Req/s",
        ],
    )
