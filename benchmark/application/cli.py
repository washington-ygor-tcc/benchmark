import click

from benchmark.application import app
from benchmark.application import helpers


@click.command()
@click.option(
    "--type",
    "-t",
    "benchmark_type",
    type=click.Choice(helpers.BenchmarkTypes),
    default=helpers.BenchmarkTypes.API,
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
def run(benchmark_type, requests_number, csv):
    results = app.run_benchmark(
        benchmark_type,
        ({"id": _} for _ in range(requests_number)),
    )
    if csv:
        app.save_benchmark_csv(benchmark_type, results, dest=csv)
    else:
        print(helpers.string_table_result(results))
