import click
import tqdm

from benchmark.application import app


def progress_indicator(progress_bar: tqdm.tqdm, current: int):
    progress_bar.update(current)


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
@click.option(
    "--m",
    type=int,
    help="specify the number of request predictions the benchmark will make",
)
def run(type, n, m):
    benchmark = app.create_benchmark(type)

    with tqdm.tqdm(total=n, desc="Running benchmark", colour="green") as pbar:
        app.run_benchmark(
            benchmark,
            ({} for _ in range(n)),
            lambda current, _: progress_indicator(pbar, current),
        )
    # app.save_benchmark(benchmark)

    print(app.calculate_avarage(benchmark))
