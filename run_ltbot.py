""" Run Bot

Main run file for Lichess Twitch Bot.

run_bot.py
"""

import sys
import logging
import argparse as ap
from pathlib import Path
from typing import List

from ltbot import load_configuration, setup_logging
from ltbot import LTBotManager


__version__ = "0.0.1"

LOG = logging.getLogger(__name__)


def parse_args(main_args: List[str]):
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
    parser.add_argument(
        "--upgrade_lichess", action="store_true", help="upgrade lichess account to bot"
    )
    args = parser.parse_args(main_args[1:])

    LOG.debug("arguments parsed")

    return args


def main(main_args: List[str]):
    """
    Main program function.
    """
    # Base setup
    args = parse_args(main_args)
    setup_logging(args.verbose)

    # Configuration setup
    configuration = load_configuration(args.configuration)

    # Initialize bot
    bot_manager = LTBotManager(configuration=configuration, version=__version__)

    # Check if Lichess account is bot
    user_profile = bot_manager.lichess_bot.get_profile()
    lichess_is_bot = user_profile.get("title") == "BOT"
    if not lichess_is_bot and args.upgrade_lichess:
        lichess_is_bot = bot_manager.upgrade_lichess_account()

    # Start bot
    if lichess_is_bot:
        bot_manager.start()
    else:
        LOG.error(
            "Can't start bot because {} is not a Lichess bot account".format(
                user_profile["username"]
            )
        )


if __name__ == "__main__":
    main(sys.argv)
