import enum
import os
import time
import pkg_resources
import yaml
import collections.abc
import tabulate
import statistics
import datetime

from typing import Any, Callable, Dict, Union, Tuple, List, TypedDict

from benchmark.core.adapters import (
    NatsMessagingAdapter,
    UUIDProviderAdapter,
    TimeProviderAdapter,
    ClientApiRestAiohttpAdapter,
)


from benchmark.core.ports import (
    IdProviderPort,
    RequestPredictionPort,
    TimeProviderPort,
)

from benchmark.core.domain import PredictionRequest


__benchmark_adapters = Tuple[RequestPredictionPort, TimeProviderPort, IdProviderPort]


class APIConfig(TypedDict):
    host: str
    port: int
    prediction_route: str


class MassagingConfig(TypedDict):
    host: str
    port: int
    request_channel: str
    response_channel: str


class Config(TypedDict):
    API: APIConfig
    MSG: MassagingConfig


@enum.unique
class BenchmarkTypes(str, enum.Enum):
    API = "API"
    MSG = "MSG"


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
    benchmark_type: BenchmarkTypes, config: Config
) -> __benchmark_adapters:
    if benchmark_type == BenchmarkTypes.MSG:
        nats_config = config[BenchmarkTypes.MSG]

        id_provider = UUIDProviderAdapter()
        time_provider = TimeProviderAdapter()
        nats_url = "{}:{}".format(nats_config["host"], nats_config["port"])

        messaging_adapter = NatsMessagingAdapter.create(
            nats_url,
            nats_config["request_channel"],
            nats_config["response_channel"],
        )

        return messaging_adapter, time_provider, id_provider

    if benchmark_type == BenchmarkTypes.API:
        api_config = config[BenchmarkTypes.API]

        client_api = ClientApiRestAiohttpAdapter(
            "{}:{}{}".format(
                api_config["host"],
                api_config["port"],
                api_config["prediction_route"],
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


def stats(results: List[PredictionRequest], start: float, end: float):
    total_time = end - start
    times = [result.end - result.start for result in results]

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
            "Total time (s)",
            "Min",
            "Max",
            "Mean",
            "STD",
            "Req/s",
        ],
    )


def batch_generator(
    next_request: Callable[[int, float], Dict[str, Any]],
    total: int = None,
    runtime: float = None,
    batch_size: int = 1,
    interval: float = 0,
):
    end = runtime and (datetime.datetime.now() + datetime.timedelta(seconds=runtime))
    requests_counter = 0

    while True:
        if total is not None and requests_counter >= total:
            break
        if runtime is not None and datetime.datetime.now() >= end:
            break

        batch = [
            next_request(iteration, datetime.datetime.now())
            for iteration in range(requests_counter, requests_counter + batch_size)
        ]

        requests_counter += batch_size

        yield batch

        time.sleep(interval)
