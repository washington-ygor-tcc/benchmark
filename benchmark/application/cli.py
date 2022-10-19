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
@click.option(
    "--csv",
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    default=".",
)
def run(benchmark_type, requests_number, csv):
    results = app.run_benchmark(
        benchmark_type,
        ({"id": _} for _ in range(requests_number)),
    )
    app.save_benchmark_csv(benchmark_type, results, dest=csv)
