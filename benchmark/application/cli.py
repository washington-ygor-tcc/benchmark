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
    help="specify the target comunication for the benchmark",
)
@click.option(
    "--requests-number",
    "-n",
    "requests_number",
    type=int,
    default=None,
    help="specify the number of request predictions the benchmark will make",
)
@click.option(
    "--runtime",
    "-r",
    type=float,
    default=None,
    help="specify the batch size the benchmark will make",
)
@click.option(
    "--batch-size",
    "-b",
    type=int,
    default=100,
    help="specify the batch size the benchmark will make",
)
@click.option(
    "--interval",
    "-i",
    type=float,
    default=0,
    help="specify the batch size the benchmark will make",
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
def run(
    benchmark_types, requests_number, runtime, batch_size, interval, csv, table, stats
):
    def _run(benchmark_type):
        results, start, end = app.run_benchmark(
            benchmark_type,
            helpers.batch_generator(
                lambda iteration, time: {"id": iteration},
                batch_size=batch_size,
                interval=interval,
                total=requests_number,
                runtime=runtime,
            ),
            total=requests_number,
            show_total_progress_bar=requests_number is not None,
            show_batch_progress_bar=True,
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
