import os
import asyncio
import uvloop
import time

from tqdm.auto import tqdm
from typing import List, Union
from benchmark.application import helpers, config as app_config
from benchmark.application.types import (
    BenchmarkTypes,
    APIConfig,
    BenchmarkParams,
    BenchmarkResult,
)
from benchmark.core.adapters import (
    CSVMetricRepositoryAdapter,
    UUIDProviderAdapter,
)
from benchmark.core.use_cases import (
    run_benchmark_use_case,
    save_benchmark_use_case,
)
from benchmark.core.domain import PredictionRequest


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

lu = helpers.get_benchmark_adapters(
    BenchmarkTypes.API, APIConfig(host="a", port=90, prediction_route="a")
)


def run_benchmark(
    params: BenchmarkParams,
    enviroment: app_config.Env = app_config.Env.LOCAL,
) -> BenchmarkResult:

    config = app_config.get_default_config(enviroment=enviroment).get(
        params.benchmark_type
    )

    adapters = helpers.get_benchmark_adapters(params.benchmark_type, config)

    results = []

    request_generator = helpers.batch_generator(
        lambda iteration, time: {
            "complexity_factor": params.complexity_factor,
            "memory_overhead": params.memory_overhead,
        },
        batch_size=params.batch_size,
        interval=params.interval,
        total=params.requests_number,
        runtime=params.runtime,
    )

    start = time.perf_counter()

    with tqdm(
        total=params.requests_number,
        desc="Total",
        disable=not params.total_progress,
    ) as progress_bar:
        for iteration, batch in enumerate(request_generator, start=1):
            tasks = [
                run_benchmark_use_case.run(features, *adapters)
                for features in batch
            ]
            batch_result = asyncio.get_event_loop().run_until_complete(
                tqdm.gather(
                    *tasks,
                    desc=f"Batch - {iteration}",
                    disable=not params.batch_progress,
                )
            )
            results.extend(batch_result)
            progress_bar.update(len(batch_result))

    end = time.perf_counter()

    return BenchmarkResult(
        response_list=results,
        params=params,
        elapsed_time=round(end - start, 2),
    )


def save_benchmark_csv(
    benchmark_type: BenchmarkTypes,
    results=List[PredictionRequest],
    dest: Union[str, os.PathLike] = ".",
):
    dest = str(dest)

    if dest.endswith("/"):
        dest = dest[: -len(dest)]

    repository = CSVMetricRepositoryAdapter(
        f"{dest}/{benchmark_type}_{helpers.get_timestamp()}.csv"
    )

    save_benchmark_use_case.save(repository, results, UUIDProviderAdapter())
