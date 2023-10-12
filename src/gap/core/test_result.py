from __future__ import annotations

from gap.core.test_parameter import TestParam
from gap.core.tester import TesterConfig


class TestResultProxy:
    def __init__(self):
        pass

    def build(self, param: TestParam, config: TesterConfig) -> None:
        pass

    def set_name(self, name: str) -> None:
        pass

    def add_detail(self, detail: str) -> None:
        pass

    def set_score(self, score: float) -> None:
        pass

    def set_extra_score(self, score: float) -> None:
        pass

    def add_error(self, error_msg: Exception) -> None:
        pass


class TestResult:
    def __init__(self) -> None:
        self.proxy = TestResultProxy()
