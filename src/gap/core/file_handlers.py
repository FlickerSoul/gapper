from pathlib import Path

from gap.core.tester import Tester


class AutograderZipper:
    def __init__(self, tester: Tester) -> None:
        self._tester = tester

    def generate_zip(self, zip_file_path: Path) -> None:
        pass
