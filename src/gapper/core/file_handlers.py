from pathlib import Path
from sys import version_info
from zipfile import ZipFile
import importlib.resources

from gapper.core.tester import Tester

from tempfile import TemporaryDirectory


class AutograderZipper:
    def __init__(self, tester: Tester) -> None:
        self._tester = tester
        self.gs_setup_files = {
            "run_autograder",
            "setup.py",
            "requirements.txt",
        }
        self.ignore_folder = {"__pycache__"}
        self.ignore_files = {".pyc"}

    def generate_zip(self, zip_file_path: Path) -> None:
        with ZipFile(zip_file_path, "w") as zip_file:
            self._copy_gap_package(zip_file)
            self._copy_gs_setup(zip_file)
            self._copy_tester_pickle(zip_file)

    def _copy_gs_setup(self, zip_file: ZipFile) -> None:
        with importlib.resources.as_file(
            importlib.resources.files("gapper.gradescope.resources")
        ) as resource_folder:
            zip_file.write(
                resource_folder / f"setup-{version_info.major}.{version_info.minor}.sh",
                arcname="setup.sh",
            )

            for file in resource_folder.iterdir():
                if file.name in self.gs_setup_files:
                    self.zip_file_path(file, zip_file, resource_folder)

    def _copy_tester_pickle(self, zip_file: ZipFile) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tester.pckl"
            self._tester.dump_to(path)
            zip_file.write(path, arcname="tester.pckl")

    def zip_file_path(self, path: Path, zip_file: ZipFile, root: Path) -> None:
        if path.is_dir():
            if path.name in self.ignore_folder:
                return None

            for sub_path in path.iterdir():
                self.zip_file_path(sub_path, zip_file, root)
        else:
            if path.suffix in self.ignore_files:
                return None

            zip_file.write(path, arcname=str(path.relative_to(root)))

    def _copy_gap_package(self, zip_file: ZipFile) -> None:
        with importlib.resources.as_file(
            importlib.resources.files("gapper")
        ) as package_path:
            self.zip_file_path(package_path, zip_file, package_path.parent)
