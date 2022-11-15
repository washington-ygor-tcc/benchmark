from benchmark.application.app import run_benchmark
from benchmark.application.types import BenchmarkResult, BenchmarkParams


def run_benchmark_wrapper(params: BenchmarkParams) -> BenchmarkResult:
    results = app.run_benchmark(
        params.benchmark_type,
        helpers.batch_generator(
            lambda iteration, time: {
                "complexity_factor": params.complexity_factor,
                "memory_overhead": params.memory_overhead,
                "iter": iteration,
            },
            batch_size=params.batch_size,
            interval=params.interval,
            total=params.requests_number,
            runtime=params.runtime,
        ),
        total=params.requests_number,
        show_total_progress_bar=params.total_progress,
        show_batch_progress_bar=params.batch_progress,
    )

    return BenchmarkResult(results, params)
