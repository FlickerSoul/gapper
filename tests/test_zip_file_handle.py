from pathlib import Path
from sys import version_info
from textwrap import dedent
from zipfile import ZipFile

from gapper.core.file_handlers import AutograderZipper
from gapper.core.tester import Tester


def test_zipping(tmp_path: Path) -> None:
    zip_path = tmp_path / "test.zip"
    zipper = AutograderZipper(Tester(None))  # type: ignore
    zipper.generate_zip(zip_path)

    # test setup.sh
    with ZipFile(zip_path, "r") as zip_file:
        setup_shell = zip_file.read("setup.sh").decode()

    major, minor = version_info.major, version_info.minor

    assert setup_shell == dedent(
        f"""\
        #!/usr/bin/env bash

        set -euo pipefail

        # install python {major}.{minor}
        add-apt-repository -y ppa:deadsnakes/ppa
        apt-get update -y
        apt-get install -y software-properties-common
        apt-get install -y python{major}.{minor} python{major}.{minor}-distutils
        ln -s $(which python3.12) $(which python3)a

        # install gapper
        curl -sS https://bootstrap.pypa.io/get-pip.py | python{major}.{minor}
        pip install --upgrade setuptools wheel
        pip install -e /autograder/source
        python{major}.{minor} -m pip cache purge"""
    )
