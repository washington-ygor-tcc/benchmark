import click

from benchmark.application import app, helpers, types, config


@click.command()
@click.option(
    "--type",
    "-t",
    "benchmark_types",
    type=click.Choice(
        list(types.BenchmarkTypes),
        case_sensitive=False,
    ),
    multiple=True,
    default=[types.BenchmarkTypes.API],
    help="the target communication for the benchmark",
)
@click.option(
    "--env",
    "-e",
    type=click.Choice(
        list(config.Env),
        case_sensitive=False,
    ),
    default=config.Env.LOCAL,
    help="the enviroment config for the benchmark",
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
    help=(
        "it controls how complex the model prediction is"
        "(cf^3 time complexity and cf^2 space complexity)"
    ),
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
    env,
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
        results = app.run_benchmark(
            params=types.BenchmarkParams(
                benchmark_type=benchmark_type,
                complexity_factor=complexity_factor,
                memory_overhead=memory_overhead,
                requests_number=requests_number,
                runtime=runtime,
                batch_size=batch_size,
                interval=interval,
                batch_progress=batch_progress,
                total_progress=total_progress,
            ),
            enviroment=env,
        )

        if csv:
            app.save_benchmark_csv(
                benchmark_type, results.response_list, dest=csv
            )
        if table:
            print(helpers.string_table_result(results.response_list))
        if stats:
            print(helpers.stats(results))

    for benchmark_type in benchmark_types:
        print(benchmark_type.upper())
        _run(benchmark_type)


if __name__ == "__main__":
    run()
