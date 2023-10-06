from pathlib import Path

import typer
from typing import Annotated

app = typer.Typer()

PATH_ARG = Annotated[Path, typer.Argument(help="The path to the problem python file.")]

DEBUG_OPT = Annotated[
    bool, typer.Option("--debug", "-d", help="Whether to run in debug mode.")
]


@app.command()
def gen(
    path: PATH_ARG,
    debug: DEBUG_OPT = False,
) -> None:
    pass


@app.command()
def run(
    path: PATH_ARG,
    debug: DEBUG_OPT = False,
    sim_env: bool = False,
) -> None:
    pass


__all__ = ["app"]
