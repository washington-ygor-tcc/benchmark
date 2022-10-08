import click

from benchmark.application import app


@click.command()
@click.option(
    "--type",
    "-t",
    "benchmark_type",
    type=click.Choice(app.BenchmarkTypes),
    default=app.BenchmarkTypes.API,
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
def run(benchmark_type, requests_number):
    results = app.run_benchmark(
        benchmark_type,
        ({"id": _} for _ in range(requests_number)),
    )
    app.save_benchmark_csv(benchmark_type, results)
