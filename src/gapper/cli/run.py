"""CLI command running the problem on some example submissions."""
from gapper.cli.cli_options import (
    AutoInjectOpt,
    InjectOpt,
    MetadataOpt,
    ProblemPathArg,
    SubmissionPathArg,
    VerboseOpt,
    timed,
)
from gapper.cli.rich_test_result_output import rich_print_test_results
from gapper.cli.utils import cli_logger, setup_root_logger
from gapper.core.injection import InjectionHandler
from gapper.core.problem import Problem
from gapper.core.result_synthesizer import ResultSynthesizer
from gapper.core.tester import Tester
from gapper.gradescope.datatypes.gradescope_meta import (
    GradescopeSubmissionMetadata,
)


@timed
def run(
    path: ProblemPathArg,
    submission: SubmissionPathArg,
    metadata_path: MetadataOpt,
    auto_inject: AutoInjectOpt,
    inject: InjectOpt,
    verbose: VerboseOpt = False,
    total_score: float = 20,
) -> None:
    """Run the autograder on an example submission."""
    setup_root_logger(verbose)

    cli_logger.debug(
        f"Try loading metadata from {metadata_path and metadata_path.absolute()}"
    )
    metadata = (
        None
        if metadata_path is None
        else GradescopeSubmissionMetadata.from_file(metadata_path)
    )
    cli_logger.debug(f"Metadata loaded: {metadata}")

    total_score = metadata.assignment.total_points if metadata else total_score
    cli_logger.debug(f"Total score is set to: {total_score}")

    InjectionHandler().setup(auto_inject, inject).inject()
    cli_logger.debug("Injection setup")

    problem = Problem.from_path(path)
    cli_logger.debug("Problem loaded")

    tester = Tester(problem)
    cli_logger.debug("Tester generated from problem")

    test_results = tester.load_submission_from_path(submission).run(metadata)
    cli_logger.debug("Test results generated from tester")

    score_obtained = ResultSynthesizer(
        results=test_results, total_score=total_score
    ).synthesize_score()
    cli_logger.debug(f"Score obtained from synthesizer {score_obtained}")

    rich_print_test_results(test_results, score_obtained, total_score)
