import click

from benchmark.application import app
from benchmark.application import helpers


@click.command()
@click.option(
    "--type",
    "-t",
    "benchmark_types",
    type=click.Choice(
        helpers.BenchmarkTypes,
    ),
    multiple=True,
    default=[helpers.BenchmarkTypes.API],
    help="the target communication for the benchmark",
)
@click.option(
    "--requests-number",
    "-n",
    "requests_number",
    type=int,
    default=None,
    help="the number of request predictions to perform",
)
@click.option(
    "--runtime",
    "-r",
    type=float,
    default=None,
    help="the period of time in seconds for performing requests",
)
@click.option(
    "--batch-size",
    "-b",
    type=int,
    default=100,
    help="the batch size of requests to perform",
)
@click.option(
    "--interval",
    "-i",
    type=float,
    default=0,
    help="the interval between requests in seconds",
)
@click.option(
    "--complexity-factor",
    "-cf",
    type=int,
    default=3,
    help="it controls how complex the model prediction is (cf^3 time complexity and cf^2 space complexity)",
)
@click.option(
    "--memory-overhead",
    "-mo",
    type=int,
    default=1,
    help="it increments the memory usage of the model prediction by mo^2",
)
@click.option(
    "--csv",
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    default=None,
)
@click.option("--table", is_flag=True)
@click.option("--stats", is_flag=True)
@click.option("--batch-progress", "-bp", is_flag=True)
@click.option("--total-progress", "-tp", is_flag=False, default=True)
def run(
    benchmark_types,
    requests_number,
    runtime,
    batch_size,
    interval,
    complexity_factor,
    memory_overhead,
    csv,
    table,
    stats,
    batch_progress,
    total_progress,
):
    def _run(benchmark_type):
        results, start, end = app.run_benchmark(
            benchmark_type,
            helpers.batch_generator(
                lambda iteration, time: {
                    "complexity_factor": complexity_factor,
                    "memory_overhead": memory_overhead,
                    "iter": iteration,
                },
                batch_size=batch_size,
                interval=interval,
                total=requests_number,
                runtime=runtime,
            ),
            total=requests_number,
            show_total_progress_bar=requests_number is not None and total_progress,
            show_batch_progress_bar=batch_progress,
        )

        if csv:
            app.save_benchmark_csv(benchmark_type, results, dest=csv)
        if table:
            print(helpers.string_table_result(results))
        if stats:
            print(helpers.stats(results, start, end))

    for benchmark_type in benchmark_types:
        print(benchmark_type.upper())
        _run(benchmark_type)


if __name__ == "__main__":
    run()
