""" Run Bot

Main run file for Lichess Twitch Bot.

run_bot.py
"""

import sys
import logging
import argparse as ap
from pathlib import Path

from ltbot import load_configuration, setup_logging
from ltbot import LichessTwitchBot


LOG = logging.getLogger(f"{__name__}")


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
        help="Each v/verbose increases the console logging level [v/vv/vvv]",
    )
    args = parser.parse_args(main_args[1:])

    return args


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
