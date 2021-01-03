import logging
from requests import get
from irc.bot import SingleServerIRCBot
from irc.client import ServerConnection, Event

from . import Lichess


LOG = logging.getLogger(__name__)


class LichessTwitchBot(SingleServerIRCBot):
    """A Twitch bot that can play chess on Lichess

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
    on_welcome(connection: ServerConnection, event: Event)
        Callback for when the bot joins the Twitch chat
    on_pubmsg(connection: ServerConnection, event: Event)
        Callback for when a chat message is received in the Twitch chat
    send_message(message: str)
        Sends a message to the Twitch chat
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

        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.USERNAME = configuration["twitch"]["username"].lower()
        self.CLIENT_ID = configuration["twitch"]["client_id"]
        self.TOKEN = configuration["twitch"]["token"]
        self.CHANNEL = "#{}".format(configuration["twitch"]["owner"].lower())

        url = f"https://api.twitch.tv/kraken/users?login={self.USERNAME}"
        headers = {
            "Client-ID": self.CLIENT_ID,
            "Accept": "application/vnd.twitchtv.v5+json",
        }
        resp = get(url, headers=headers).json()
        self.channel_id = resp["users"][0]["_id"]

        super().__init__(
            [(self.HOST, self.PORT, f"oauth:{self.TOKEN}")],
            self.USERNAME,
            self.USERNAME,
        )

        self.lichess_bot = Lichess(
            token=configuration["lichess"]["token"],
            url=configuration["lichess"]["url"],
            version=version,
        )
        user_profile = self.lichess_bot.get_profile()
        LOG.info("Connected user {} to lichess".format(user_profile["username"]))

        LOG.debug("ltbot initialized")

    def upgrade_lichess_account(self) -> bool:
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

    def on_welcome(self, connection: ServerConnection, event: Event):
        """Callback for when connection has been established

        Joins the Twitch chat and sends a message to confirm
        connection.

        Parameters
        ----------
        connection : ServerConnection
            Connection to Twitch server
        event : Event
            Event object for connection
        """

        for req in ("membership", "tags", "commands"):
            connection.cap("REQ", f":twitch.tv/{req}")

        connection.join(self.CHANNEL)
        self.send_message("Connected")
        LOG.info(f"Connected user {self.USERNAME} to twitch channel {self.CHANNEL[1:]}.")

    def on_pubmsg(self, connection: ServerConnection, event: Event):
        """Callback for when message is received

        Reads the message and handles it if needed.

        Parameters
        connection : ServerConnection
            Connection to Twitch server
        event : Event
            Event object for connection
        ----------
        """

        tags = {kvpair["key"]: kvpair["value"] for kvpair in event.tags}
        user = {"name": tags["display-name"], "id": tags["user-id"]}
        message = event.arguments[0]

        LOG.info(f"Message from {user['name']}: {message}")

    def send_message(self, message: str):
        """Sends message to chat

        Sends a message to chat and logs it.

        Parameters
        ----------
        message : str
            The message to send
        """

        LOG.debug("Sending message: {}".format(message))
        self.connection.privmsg(self.CHANNEL, message)

    def start(self):
        """Start bot

        Starts the bot and writes to log.
        """

        LOG.debug("Starting bot")
        super().start()

    def stop(self):
        """Stop bot

        Stops the bot and writes to log.
        """

        LOG.debug("Stopping bot")
        self.die()
