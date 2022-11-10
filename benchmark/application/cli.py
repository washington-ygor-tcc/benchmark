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
    "--feature-size",
    "-f",
    type=int,
    default=0,
    help="a feature parameter to controll the complexity of the prediction",
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
    feature_size,
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
                lambda iteration, time: {"feature_size": feature_size, "iter": iteration},
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
