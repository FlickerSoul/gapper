"""A module to handle the autograder zip file generation."""
import importlib.resources
import logging
from pathlib import Path
from sys import version_info
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import jinja2

from gapper.core.tester import Tester
from gapper.gradescope.vars import DEFAULT_TESTER_PICKLE_NAME

_zip_logger = logging.getLogger("gapper.zip")


class AutograderZipper:
    def __init__(self, tester: Tester) -> None:
        """A class to generate the autograder zip file.

        :param tester: The tester to generate the autograder for.
        """
        self._tester = tester
        self.gs_setup_files = {
            "run_autograder",
            "setup.py",
            "requirements.txt",
        }
        self.ignore_folder = {"__pycache__"}
        self.ignore_files = {".pyc", ".DS_Store", ".j2"}

    def generate_zip(self, zip_file_path: Path) -> None:
        """Generate the autograder zip file given a save path.

        :param zip_file_path: The path to save the zip file.
        """
        with ZipFile(zip_file_path, "w") as zip_file:
            self._copy_gap_package(zip_file)
            self._copy_gs_setup(zip_file)
            self._copy_tester_pickle(zip_file)

        _zip_logger.debug(
            f"Completed autograder zip file at {zip_file_path.absolute()}."
        )

    def _copy_gs_setup(self, zip_file: ZipFile) -> None:
        with importlib.resources.as_file(
            importlib.resources.files("gapper.gradescope.resources")
        ) as resource_folder:
            with open(resource_folder / "setup.j2", "r") as setup_file:
                template_content = setup_file.read()
                setup_sh_template = jinja2.Template(template_content)

            setup_shell_script = setup_sh_template.render(
                py_minor=version_info.minor, py_major=version_info.major
            )

            zip_file.writestr("setup.sh", setup_shell_script)

            for file in resource_folder.iterdir():
                if file.name in self.gs_setup_files:
                    self.zip_file_path(file, zip_file, resource_folder)

            _zip_logger.debug("Copied gs setup files into zip file.")

    def _copy_tester_pickle(self, zip_file: ZipFile) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / DEFAULT_TESTER_PICKLE_NAME
            self._tester.dump_to(path)
            zip_file.write(path, arcname=DEFAULT_TESTER_PICKLE_NAME)

        _zip_logger.debug("Copied tester pickle into zip file.")

    def zip_file_path(self, path: Path, zip_file: ZipFile, root: Path) -> None:
        """Zip a file or folder.

        :param path: The path to the file to be zipped into.
        :param zip_file: The zip file to zip the file from <path> into.
        :param root: The root path.
        """
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

        _zip_logger.debug("Copied gapper package into zip file.")
