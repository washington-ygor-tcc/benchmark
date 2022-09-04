import click

from benchmark.application import app


@click.command()
@click.option(
    "--type",
    type=click.Choice(app.BenchmarkTypes),
    default=app.BenchmarkTypes.API,
    help="specify the target comunication for the benchmark",
)
@click.option(
    "--n",
    type=int,
    required=True,
    help="specify the number of request predictions the benchmark will make",
)
def run(type, n):
    results = app.run_benchmark(
        type,
        ({"id": _} for _ in range(n)),
    )
