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

    version_short = f"{major}.{minor}"

    assert setup_shell == dedent(
        f"""\
        #!/usr/bin/env bash

        set -euo pipefail

        # install python {version_short}
        add-apt-repository -y ppa:deadsnakes/ppa
        apt-get update -y
        apt-get install -y software-properties-common
        apt-get install -y python{version_short} python{version_short}-distutils
        ln -s $(which python{version_short}) $(which python3).gapper

        # install gapper
        curl -sS https://bootstrap.pypa.io/get-pip.py | python{version_short}
        pip install --upgrade setuptools wheel
        pip install -e /autograder/source
        python{version_short} -m pip cache purge"""
    )
