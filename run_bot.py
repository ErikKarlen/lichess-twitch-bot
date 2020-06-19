""" Run Bot

Main run file for Lichess Twitch Bot.

run_bot.py
"""

import sys
import logging
import argparse as ap
from pathlib import Path
import yaml

from lichess_twitch_bot import LichessTwitchBot

LOG = logging.getLogger(f"tlb.{Path(__file__).stem}")


def setup_logging(logging_level):
    """
    Setup logging
    """
    # Logging to file
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%y-%m-%d %H:%M",
        filename=f"{__file__}.log",
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
    console.setFormatter(logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s"))
    logging.getLogger("").addHandler(console)

    LOG.debug("Logger setup")


def parse_args(main_args):
    """
    Parse arguments
    """
    parser = ap.ArgumentParser(description="Starts a Lichess Twitch Bot")
    parser.add_argument("-c", "--configuration", type=str, help="configuration file", required=True)
    parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        action="count",
        help="Each v increases the console logging level [v/vv/vvv]",
    )
    args = parser.parse_args(main_args[1:])

    return args


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


def main(main_args):
    """
    Main program function.
    """
    # Base setup
    args = parse_args(main_args)
    setup_logging(args.verbose)
    configuration = load_configuration(args.configuration)

    username = configuration["twitch"]["username"]
    owner = configuration["twitch"]["owner"]
    client_id = configuration["twitch"]["client_id"]
    token = configuration["twitch"]["token"]

    # Start bot
    bot = LichessTwitchBot(username, owner, client_id, token)
    bot.start()


if __name__ == "__main__":
    main(sys.argv)
