"""Setup file for gapper autograder in the production environment."""
from setuptools import setup  # type: ignore


def parse_requirements(file: str) -> list[str]:
    """Parse requirements.txt file."""
    with open(file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def get_version() -> str:
    """Get the version from _version.py."""
    with open("gapper/_version.py", "r", encoding="utf-8") as f:
        for line in f.readlines():
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"')

    raise ValueError("Version not found.")


setup(
    name="gapper",
    version=get_version(),
    install_requires=parse_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "gapper = gapper.cli:app",
            "gap = gapper.cli:app",
            "gradescope-autograder-packer = gapper.cli:app",
        ]
    },
)
