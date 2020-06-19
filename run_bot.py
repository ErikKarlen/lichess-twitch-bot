""" Run Bot

Main run file for Lichess Twitch Bot.

run_bot.py
"""

import sys
import argparse as ap
from pathlib import Path
import yaml

from lichess_twitch_bot import LichessTwitchBot


def parse_args(main_args):
    """
    Parse arguments
    """
    parser = ap.ArgumentParser(description="Starts a Lichess Twitch Bot")
    parser.add_argument("-c", "--configuration", type=str, help="configuration file", required=True)
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

    return configuration


def main(main_args):
    """
    Main program function.
    """
    # Basic setup
    args = parse_args(main_args)
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
