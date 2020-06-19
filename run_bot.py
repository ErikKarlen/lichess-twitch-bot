""" Run Bot

Main run file for Lichess Twitch Bot.

run_bot.py
"""

import sys
import argparse as ap
from pathlib import Path
import yaml

from lichess_twitch_bot import LichessTwitchBot


def main(main_args):
    """
    Main program function.
    """

    # Setup argument parser
    parser = ap.ArgumentParser(description="Starts a Lichess Twitch Bot")
    parser.add_argument("-c", "--configuration", type=str, help="configuration file", required=True)
    args = parser.parse_args(main_args[1:])

    # Load configuration
    configuration_path = Path(args.configuration)
    with open(configuration_path, "r") as configuration_stream:
        try:
            configuration = yaml.safe_load(configuration_stream)
        except yaml.YAMLError as exc:
            print(exc)

    # Start bot
    bot = LichessTwitchBot(configuration["twitch"]["client_id"], configuration["twitch"]["token"])
    bot.start()


if __name__ == "__main__":
    main(sys.argv)
