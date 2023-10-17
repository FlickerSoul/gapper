from setuptools import setup  # type: ignore


def parse_requirements(file: str) -> list[str]:
    with open(file) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def get_version() -> str:
    with open("gapper/_version.py") as f:
        for line in f.readlines():
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"')


setup(
    name="gapper",
    version=get_version(),
    install_requires=parse_requirements("requirements.txt"),
)
