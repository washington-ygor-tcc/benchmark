import asyncio
import click

from benchmark.application import app


@click.command()
@click.option(
    "--type",
    type=click.Choice(app.BenchmarkTypes),
    default=app.BenchmarkTypes.API,
    help="specify the target comunication for the benchmark",
)
@click.option("--n", type=int, required=True)
def cli(type, n):
    benchmark = app.create_benchmark(type, n)

    benchmark = asyncio.run(benchmark)

    print(app.calculate_avarage(benchmark))
