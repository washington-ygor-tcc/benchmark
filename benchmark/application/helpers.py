import time
import tabulate
import statistics
import datetime

from typing import (
    Any,
    Callable,
    Dict,
    Tuple,
    List,
)

from benchmark.application.types import (
    BenchmarkTypes,
    BenchmarkResult,
    BenchmarkTypesLiteral,
)

from benchmark.core.adapters import (
    NatsMessagingAdapter,
    UUIDProviderAdapter,
    TimeProviderAdapter,
    ClientApiRestAiohttpAdapter,
)

from benchmark.core.types import APIConfig, MessagingConfig

from benchmark.core.ports import (
    IdProviderPort,
    RequestPredictionPort,
    TimeProviderPort,
)
from benchmark.core.domain import PredictionRequest


__BENCHMARK_ADAPTERS = Tuple[
    RequestPredictionPort, TimeProviderPort, IdProviderPort
]

__REQUEST_ADAPTERS: dict[BenchmarkTypes, Callable] = {
    BenchmarkTypes.MSG: NatsMessagingAdapter.create,
    BenchmarkTypes.API: ClientApiRestAiohttpAdapter.create,
}


def get_benchmark_adapters(
    benchmark_type: BenchmarkTypesLiteral,
    config: APIConfig | MessagingConfig,
) -> __BENCHMARK_ADAPTERS:

    if benchmark_type not in BenchmarkTypes:
        raise NotImplementedError

    id_provider = UUIDProviderAdapter()
    time_provider = TimeProviderAdapter()
    request_adapter = __REQUEST_ADAPTERS[benchmark_type](config)

    return request_adapter, time_provider, id_provider


def get_timestamp():
    return datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")


def string_table_result(results: List[PredictionRequest]) -> str:
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


def stats(results: BenchmarkResult):
    response_list = results.response_list
    times = [
        result.end - result.start
        for result in response_list
        if result.end and result.start
    ]

    return tabulate.tabulate(
        [
            [
                len(response_list),
                results.elapsed_time,
                min(times),
                max(times),
                statistics.mean(times),
                statistics.stdev(times),
                len(response_list) / results.elapsed_time,
            ]
        ],
        headers=[
            "Nº Requests",
            "Total time (s)",
            "Min (s)",
            "Max (s)",
            "Mean (s)",
            "STD",
            "Req/s",
        ],
    )


def batch_generator(
    next_request: Callable[[int, datetime.datetime], Dict[str, Any]],
    total: int | None = None,
    runtime: float | None = None,
    batch_size: int = 1,
    interval: float = 0,
):
    stop_at = runtime is not None and (
        datetime.datetime.now() + datetime.timedelta(seconds=runtime)
    )
    requests_counter = 0

    while True:
        if total is not None and requests_counter >= total:
            break
        if stop_at and datetime.datetime.now() >= stop_at:
            break

        limit = (
            requests_counter + batch_size
            if total is None
            else requests_counter + min(batch_size, total)
        )

        batch = [
            next_request(iteration, datetime.datetime.now())
            for iteration in range(requests_counter, limit)
        ]

        requests_counter += batch_size

        yield batch

        time.sleep(interval)
