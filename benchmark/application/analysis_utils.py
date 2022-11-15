from benchmark.application.app import run_benchmark
from benchmark.application.helpers import batch_generator
from benchmark.application.types import BenchmarkResult, BenchmarkParams, BenchmarkTypes


config = {
    BenchmarkTypes.API: {"API": {"host": "http://api"}},
    BenchmarkTypes.MSG: {"MSG": {"host": "nats://broker"}},
}


def run_benchmark_wrapper(params: BenchmarkParams) -> BenchmarkResult:
    results, start, end = run_benchmark(
        benchmark_type=params.benchmark_type,
        request_generator=batch_generator(
            lambda iteration, time: {
                "complexity_factor": params.complexity_factor,
                "memory_overhead": params.memory_overhead,
            },
            batch_size=params.batch_size,
            interval=params.interval,
            total=params.requests_number,
            runtime=params.runtime,
        ),
        total=params.requests_number,
        config=config[params.benchmark_type],
        show_total_progress_bar=params.batch_progress,
        show_batch_progress_bar=params.total_progress,
    )

    return BenchmarkResult(
        response_list=results, params=params, elapsed_time=round(end - start, 2)
    )
