"""Run Lichess Twitch Bot

This script lets the user start a Twitch bot that can be used for
controlling a Lichess account playing a game of chess.

This file can als be imported as a module and contains the following
functions:

    * signal_handler - Handles signals and exits program
    * exit - Stops the bot and exits program
    * parse_args - Parses arguments
    * main - Can be used for starting a Lichess Twitch Bot

    COPYRIGHT INFORMATION
    ---------------------
Based on the twitch bot tutorial by Carberra.
    https://github.com/Carberra/twitch-bot-tutorial/blob/master/twitch_tut.py
Some code in this file is licensed under the Apache License, Version 2.0.
    http://aws.amazon.com/apache2.0/
"""

import sys
import signal
import logging
import argparse as ap
from pathlib import Path
from typing import List

from ltbot import load_configuration, setup_logging
from ltbot import LTBotManager


__version__ = "0.0.1"

LOG = logging.getLogger(__name__)


def signal_handler(signum: int, frame, bot_manager: LTBotManager):
    """Signal handling

    Parameters
    ----------
    signum : int
        Number representation of the signal received
    frame
        The current call frame when the signal was received
    bot_manager : LTBotManager
        Manager of a Lichess Twitch Bot
    """

    signal_name = signal.Signals(signum).name
    LOG.debug(f"Handling {signal_name} signal")
    exit(bot_manager)


def exit(bot_manager: LTBotManager):
    """Exit program

    Parameters
    ----------
    bot_manager : LTBotManager
        Manager of a Lichess Twitch Bot
    """

    LOG.debug("Exiting program")
    bot_manager.stop()
    sys.exit()


def parse_args(main_args: List[str]):
    """Parse arguments

    Parameters
    ----------
    main_args : List[str]
        List of arguments
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
    """Main program function

    Parameters
    ----------
    main_args: List[str]
        List of arguments
    """

    # Base setup
    args = parse_args(main_args)
    setup_logging(args.verbose)

    # Configuration setup
    configuration = load_configuration(Path(args.configuration))

    # Initialize bot
    bot_manager = LTBotManager(configuration=configuration, version=__version__)

    # Setup signal handling
    signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, bot_manager))

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
