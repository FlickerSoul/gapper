import logging

_package_logger = logging.getLogger("gapper")


def setup_root_logger(verbose: bool) -> None:
    """Set up the root logger.

    :param verbose: Whether to run in verbose mode.
    """
    level = logging.DEBUG if verbose else logging.INFO
    _package_logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    # add formatter to ch
    ch.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # add ch to logger
    _package_logger.addHandler(ch)

    _package_logger.debug(f"Set up root logger with level {level}.")
