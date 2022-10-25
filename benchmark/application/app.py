import os
import asyncio
import tqdm.auto
import uvloop

from typing import Dict, List, Union
from benchmark.application import helpers
from benchmark.core.adapters.metric_repository_adapter import (
    MetricRepositoryAdapter,
)
from benchmark.core.use_cases import benchmark
from benchmark.core.types import (
    RequestGenerator,
)
from benchmark.core.domain.prediction_request import PredictionRequest

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def run_benchmark(
    benchmark_type: helpers.BenchmarkTypes,
    request_generator: RequestGenerator,
    config: Dict = {},
    show_progress_bar: bool = True,
) -> List[PredictionRequest]:

    config_with_defaults = helpers.update_config(
        config, helpers.get_default_config()
    )
    adapters = helpers.get_benchmark_adapters(
        benchmark_type, config_with_defaults
    )

    tasks = [
        benchmark.run(features, *adapters) for features in request_generator
    ]

    return asyncio.run(
        tqdm.auto.tqdm.gather(*tasks, disable=not show_progress_bar)
    )


def save_benchmark_csv(
    benchmark_type: helpers.BenchmarkTypes,
    results=List[PredictionRequest],
    dest: Union[str, os.PathLike] = ".",
):

    if dest.endswith("/"):
        dest = dest[: -len(dest)]

    repository = MetricRepositoryAdapter(
        f"{dest}/{benchmark_type}_{helpers.get_timestamp()}.csv"
    )
    benchmark.save(repository, results)
