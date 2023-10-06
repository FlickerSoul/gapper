from __future__ import annotations

from pathlib import Path

from gap.core.tester import TesterConfig

from dacite import from_dict, Config

import tomllib


def load_tester_config_from_file(path: Path, with_default: bool = True) -> TesterConfig:
    try:
        with open(path, "rb") as file:
            return from_dict(
                data_class=TesterConfig,
                data=tomllib.load(file),
                config=Config(cast=[Path, set]),
            )
    except FileNotFoundError as e:
        if with_default:
            return TesterConfig()
        else:
            raise FileNotFoundError(f"File {path} not found.") from e
