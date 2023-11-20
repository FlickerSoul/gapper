from gapper.core.test_result import TestResult
from gapper.core.tester.hook import HookBase, HookTypes
from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata


class PreTest(HookBase):
    _hook_type = HookTypes.PRE_TEST

    def __repr__(self) -> str:
        """Return the representation of the pre-test."""
        return f"PreTest(hook_fn={self.hook_fn}, as_test_case={self.as_test_case})"

    def _run(
        self,
        *args,
        result_proxy: TestResult | None,
        metadata: GradescopeSubmissionMetadata | None,
    ) -> None:
        self.hook_fn(result_proxy, metadata)


pre_test = PreTest
