import typer

from .check import check
from .gen import gen
from .login import login
from .run import run
from .run_in_prod import run_in_prod
from .upload import upload

command_impls = [check, run, run_in_prod, upload, login, gen]

app = typer.Typer()
for command_impl in command_impls:
    app.command()(command_impl)


__all__ = ["app"]
