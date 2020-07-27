""" Lichess Twitch Bot Manager

Manages Lichess and Twitch connections

ltbot_manager.py
"""

import logging

from . import LichessTwitchBot, Lichess


LOG = logging.getLogger(__name__)


class LTBotManager:
    def __init__(self, configuration: dict, version: str):
        self.configuration = configuration

        self.twitch_bot = LichessTwitchBot(
            username=configuration["twitch"]["username"],
            owner=configuration["twitch"]["owner"],
            client_id=configuration["twitch"]["client_id"],
            token=configuration["twitch"]["token"],
        )

        self.lichess_bot = Lichess(
            token=configuration["lichess"]["token"],
            url=configuration["lichess"]["url"],
            version=version,
        )
        user_profile = self.lichess_bot.get_profile()
        LOG.info("Connected user {} to lichess".format(user_profile["username"]))

    def upgrade_lichess_account(self):
        if self.lichess_bot.upgrade_to_bot_account() is None:
            return False

        LOG.info("Succesfully upgraded Lichess account to bot")
        return True

    def start(self):
        self.twitch_bot.start()
