import sys

from lichess_twitch_bot import LichessTwitchBot

def main(main_args):
    bot = LichessTwitchBot()
    bot.start()


if __name__ == "__main__":
    main(sys.argv)