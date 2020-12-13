import logging

from . import LichessTwitchBot, Lichess


LOG = logging.getLogger(__name__)


class LTBotManager:
    """Lichess Twitch Bot Manager

    Manages Lichess and Twitch connections.

    ---

    Attributes
    ----------
    configuration : dict
        Dictionary with Twitch and Lichess configuration
    version : str
        String representation of bot version

    Methods
    -------
    upgrade_lichess_account()
        Upgrades the connected Lichess account to bot
    start()
        Starts the bot
    stop()
        Stops the bot
    """

    def __init__(self, configuration: dict, version: str):
        """
        Parameters
        ----------
        configuration : dict
            Dictionary with Twitch and Lichess configuration
        version : str
            String representation of bot version
        """

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
        """Upgrade Lichess account to bot account

        Returns
        -------
        bool
            Returns True if successful, otherwise False
        """

        if self.lichess_bot.upgrade_to_bot_account() is None:
            return False

        LOG.info("Succesfully upgraded Lichess account to bot")
        return True

    def start(self):
        """Start bot

        Starts the bot and writes to log.
        """

        LOG.debug("Starting bot")
        self.twitch_bot.start()

    def stop(self):
        """Stop bot

        Stops the bot and writes to log.
        """

        LOG.debug("Stopping bot")
        self.twitch_bot.die()
