import os
import asyncio
import uvloop
import time

from tqdm.auto import tqdm
from typing import List, Union
from benchmark.application import helpers, types
from benchmark.core.adapters import (
    CSVMetricRepositoryAdapter,
    UUIDProviderAdapter,
)
from benchmark.core.use_cases import (
    run_benchmark_use_case,
    save_benchmark_use_case,
)
from benchmark.core.types import RequestGenerator
from benchmark.core.domain import PredictionRequest

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def run_benchmark(
    benchmark_type: types.BenchmarkTypes,
    request_generator: RequestGenerator,
    total: int = 0,
    config: Union[helpers.APIConfig, helpers.MessagingConfig] = None,
    show_total_progress_bar: bool = True,
    show_batch_progress_bar: bool = True,
) -> List[PredictionRequest]:

    if config is None:
        config = {}

    config_with_defaults = helpers.update_config(
        config, helpers.get_default_config()
    )
    adapters = helpers.get_benchmark_adapters(
        benchmark_type, config_with_defaults
    )

    results = []

    start = time.perf_counter()

    with tqdm(
        total=total, desc="Total", disable=not show_total_progress_bar
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
                    disable=not show_batch_progress_bar,
                )
            )
            results.extend(batch_result)
            progress_bar.update(len(batch_result))

    end = time.perf_counter()

    return results, start, end


def save_benchmark_csv(
    benchmark_type: types.BenchmarkTypes,
    results=List[PredictionRequest],
    dest: Union[str, os.PathLike] = ".",
):

    if dest.endswith("/"):
        dest = dest[: -len(dest)]

    repository = CSVMetricRepositoryAdapter(
        f"{dest}/{benchmark_type}_{helpers.get_timestamp()}.csv"
    )

    save_benchmark_use_case.save(repository, results, UUIDProviderAdapter())
