""" Miscellaneous

Miscellaneous functions and constants.

misc.py
"""
import logging
import yaml
from pathlib import Path


LOGGING_FILENAME = "ltbot"
LOGGING_NAME_LENGTH = 30


def load_configuration(configuration_file):
    """
    Load program configuration
    """
    configuration_path = Path(configuration_file)
    with open(configuration_path, "r") as configuration_stream:
        try:
            configuration = yaml.safe_load(configuration_stream)
        except yaml.YAMLError as exc:
            print(exc)

    LOG.debug("Loaded configuration")

    return configuration


def setup_logging(logging_level):
    """
    Setup logging
    """
    # Logging to file
    logging.basicConfig(
        level=logging.DEBUG,
        format=f"%(asctime)s %(name)-{LOGGING_NAME_LENGTH}s %(levelname)-8s %(message)s",
        datefmt="%y-%m-%d %H:%M",
        filename=f"{LOGGING_FILENAME}.log",
        filemode="w",
    )

    # Logging to console
    console = logging.StreamHandler()
    if logging_level == 1:
        console_level = logging.WARNING
    elif logging_level == 2:
        console_level = logging.INFO
    elif logging_level == 3:
        console_level = logging.DEBUG
    else:
        console_level = logging.ERROR
    console.setLevel(console_level)
    console.setFormatter(logging.Formatter(f"%(name)-{LOGGING_NAME_LENGTH}s: %(levelname)-8s %(message)s"))
    logging.getLogger("").addHandler(console)