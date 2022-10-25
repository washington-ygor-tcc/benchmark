import asyncio
from time import sleep
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
    required=True,
    help="specify the number of request predictions the benchmark will make",
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
def run(benchmark_types, requests_number, csv, table, stats):
    def _run(benchmark_type):
        results = app.run_benchmark(
            benchmark_type,
            ({"id": i} for i in range(requests_number)),
        )
        if csv:
            app.save_benchmark_csv(benchmark_type, results, dest=csv)
        if table:
            print(helpers.string_table_result(results))
        if stats:
            print(helpers.stats(results))

    for benchmark_type in benchmark_types:
        print(benchmark_type.upper())
        _run(benchmark_type)
