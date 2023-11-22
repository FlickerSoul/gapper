"""CLI command for generating autograder zip with additional upload ability."""
import typer

from gapper.cli.cli_options import (
    AutoInjectOpt,
    InjectOpt,
    LoginSavePath,
    OverwriteConfirmOpt,
    ProblemPathArg,
    SavePathOpt,
    UIDebugOpt,
    UploadOpt,
    UseGUIOpt,
    VerboseOpt,
    timed,
)
from gapper.cli.utils import (
    cli_logger,
    setup_root_logger,
    upload_with_connect_details,
    upload_with_gui,
)
from gapper.connect.gui.utils import DEFAULT_LOGIN_SAVE_PATH, add_debug_to_app
from gapper.core.file_handlers import AutograderZipper
from gapper.core.injection import InjectionHandler
from gapper.core.problem import Problem
from gapper.core.tester import Tester


@timed
def gen(
    path: ProblemPathArg,
    autograder_save_path: SavePathOpt,
    auto_inject: AutoInjectOpt,
    inject: InjectOpt,
    confirm_overwrite: OverwriteConfirmOpt = False,
    verbose: VerboseOpt = False,
    upload_flag: UploadOpt = False,
    use_ui: UseGUIOpt = False,
    login_save_path: LoginSavePath = DEFAULT_LOGIN_SAVE_PATH,
    ui_debug: UIDebugOpt = False,
) -> None:
    """Generate the autograder for a problem."""
    add_debug_to_app(ui_debug)
    setup_root_logger(verbose)

    InjectionHandler().setup(auto_inject, inject).inject()
    cli_logger.debug("Injection setup")

    problem = Problem.from_path(path)
    cli_logger.debug("Problem loaded")

    tester = Tester(problem)
    cli_logger.debug("Tester generated from problem")

    if autograder_save_path.is_dir():
        autograder_save_path = (
            autograder_save_path / f"{problem.expected_submission_name}.zip"
        )

    if autograder_save_path.exists() and (
        confirm_overwrite
        or typer.confirm(
            f"File {autograder_save_path.absolute()} already exists. Overwrite?",
            default=True,
            abort=True,
        )
    ):
        typer.echo("Overwriting...")

    AutograderZipper(tester).generate_zip(autograder_save_path)
    typer.echo(
        f"Autograder zip generated successfully at {autograder_save_path.absolute()}"
    )

    if upload_flag:
        if use_ui:
            upload_with_gui(login_save_path, autograder_save_path)
        else:
            if problem.config.extras["gs_connect"] is not None:
                gs_connect = problem.config.extras["gs_connect"]
                upload_with_connect_details(
                    gs_connect.cid,
                    gs_connect.aid,
                    login_save_path,
                    autograder_save_path,
                )
            else:
                typer.echo(
                    "No Gradescope connection info found in problem config. "
                    "Please use @gapper.connect() decorator, or use the --gui flag."
                )
                raise typer.Exit(code=1)
