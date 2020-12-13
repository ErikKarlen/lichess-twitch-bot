import logging
import yaml
from pathlib import Path


LOG = logging.getLogger(__name__)

# Logging constants
LOGGING_FILENAME = "ltbot"
LOGGING_NAME_LENGTH = 30


def load_configuration(configuration_file: Path):
    """Load program configuration

    Loads bot configuration from yaml file returns its dict
    representation.

    Parameters
    ----------
    configuration_file : Path
        Yaml file with bot configuration

    Returns
    -------
        Dict representation of the configuration
    """

    # Convert to Path if it not already is
    if not isinstance(configuration_file, Path):
        configuration_path = Path(configuration_file)

    # Load yaml configuration file
    with open(configuration_path, "r") as configuration_stream:
        try:
            configuration = yaml.safe_load(configuration_stream)
        except yaml.YAMLError as exc:
            LOG.error("Failed to load configuration file")
            raise exc

    LOG.debug("configuration loaded")

    return configuration


def setup_logging(logging_level: int):
    """Setup logging

    Enables logging for the program.

    Parameters
    ----------
    logging_level : int
        The level to log for. Higher value gives more logging.
    """

    # Logging to file
    logging.basicConfig(
        level=logging.DEBUG,
        format=f"%(asctime)s %(name)-{LOGGING_NAME_LENGTH}s [%(levelname)-8s] %(message)s",
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
    console.setFormatter(
        logging.Formatter(f"%(name)-{LOGGING_NAME_LENGTH}s: [%(levelname)-8s] %(message)s")
    )
    logging.getLogger("").addHandler(console)

    LOG.debug("logging setup")
