from json import dumps

from rich.console import Console
from rich.table import Table
from typer import Argument, Exit, Option, Typer, echo

from _fp_devtools.estimator import CostEstimator, estimate_cost

app = Typer(
    name="pf",
    help="A CLI for the FP Devtools",
    invoke_without_command=False,
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
)


@app.callback()
def callback() -> None:
    pass


@app.command("overhead")
def compute_overhead(
    overhead_µs: float = Argument(
        ...,
        metavar="MICROSECONDS",
        help="Number of microsecond of overhead to consider.",
    ),
    n_calls_per_sec: int = Option(
        ..., "-n", "--n-calls-per-sec", help="Number of calls per second."
    ),
    json: bool = Option(False, "--json", help="Output as JSON."),
):
    """Estimate how much time will be spent on overhead per second, minute, hour, day, month, year,
    given the overhead per call and the number of calls per second."""
    cost = estimate_cost(overhead_µs, n_calls_per_sec)
    if json:
        echo(dumps(cost.to_dict(), indent=2, sort_keys=False))
        raise Exit(0)
    _display_overhead_table(cost)
    raise Exit(0)


def _display_overhead_table(cost: CostEstimator) -> None:
    console = Console()
    table = Table(
        title=f"Overhead per second, minute, hour, day, month, year\n for a given overhead per call of {cost.overhead_µs:.3f} microseconds called {cost.n_calls_per_sec} times per second."
    )
    table.add_column("Per call (microseconds)", justify="right")
    table.add_column("Calls per second", justify="right")
    table.add_column("Per second (microseconds)", justify="right")
    table.add_column("Per minute (milliseconds)", justify="right")
    table.add_column("Per hour (milliseconds)", justify="right")
    table.add_column("Per day (seconds)", justify="right")
    table.add_column("Per month (minutes)", justify="right")
    table.add_column("Per year (hours)", justify="right")
    table.add_row(*map(lambda x: format(float(x), ".3f"), cost.to_dict().values()))
    console.print(table)


if __name__ == "__main__":
    app()
