import logging
from requests import get
from pathlib import Path
from irc.bot import SingleServerIRCBot
from irc.client import ServerConnection, Event


LOG = logging.getLogger(__name__)


class LichessTwitchBot(SingleServerIRCBot):
    """A Twitch bot that can play chess on Lichess

    ---

    Attributes
    ----------
    username : str
        Twitch user name of the Twitch bot
    owner : str
        Twitch user name of the channel to join
    client_id : str
        The Twitch bot's client id
    token : str
        The Twitch bot's token

    Methods
    -------
    on_welcome(connection: ServerConnection, event: Event)
        Callback for when the bot joins the Twitch chat
    on_pubmsg(connection: ServerConnection, event: Event)
        Callback for when a chat message is received in the Twitch chat
    send_message(message: str)
        Sends a message to the Twitch chat
    """

    def __init__(self, username: str, owner: str, client_id: str, token: str):
        """
        Parameters
        ----------
        username : str
            Twitch user name of the Twitch bot
        owner : str
            Twitch user name of the channel to join
        client_id : str
            The Twitch bot's client id
        token : str
            The Twitch bot's token
        """

        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.USERNAME = username.lower()
        self.CLIENT_ID = client_id
        self.TOKEN = token
        self.CHANNEL = f"#{owner.lower()}"

        url = f"https://api.twitch.tv/kraken/users?login={self.USERNAME}"
        headers = {
            "Client-ID": self.CLIENT_ID,
            "Accept": "application/vnd.twitchtv.v5+json",
        }
        resp = get(url, headers=headers).json()
        self.channel_id = resp["users"][0]["_id"]

        super().__init__(
            [(self.HOST, self.PORT, f"oauth:{self.TOKEN}")], self.USERNAME, self.USERNAME,
        )
        LOG.debug("ltbot initialized")

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

        Logs the received message.

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

        LOG.debug("Sending message")
        self.connection.privmsg(self.CHANNEL, message)
