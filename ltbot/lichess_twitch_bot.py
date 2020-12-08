""" Lichess Twitch Bot

    COPYRIGHT INFORMATION
    ---------------------
Based on the twitch bot tutorial by Carberra.
    https://github.com/Carberra/twitch-bot-tutorial/blob/master/twitch_tut.py
Some code in this file is licensed under the Apache License, Version 2.0.
    http://aws.amazon.com/apache2.0/

lichess_twitch_bot.py
"""

import logging
from requests import get
from pathlib import Path
from irc.bot import SingleServerIRCBot
from irc.client import ServerConnection, Event


LOG = logging.getLogger(__name__)


class LichessTwitchBot(SingleServerIRCBot):
    def __init__(self, username: str, owner: str, client_id: str, token: str):
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

    def on_welcome(self, connection, event):
        """
        Callback for when connection has been established
        """
        for req in ("membership", "tags", "commands"):
            connection.cap("REQ", f":twitch.tv/{req}")

        connection.join(self.CHANNEL)
        self.send_message("Connected")
        LOG.info(f"Connected user {self.USERNAME} to twitch channel {self.CHANNEL[1:]}.")

    def on_pubmsg(self, connection: ServerConnection, event: Event):
        """
        Callback for when message is received
        """
        tags = {kvpair["key"]: kvpair["value"] for kvpair in event.tags}
        user = {"name": tags["display-name"], "id": tags["user-id"]}
        message = event.arguments[0]

        LOG.info(f"Message from {user['name']}: {message}")

    def send_message(self, message: str):
        """
        Sends message to chat
        """
        LOG.debug("Sending message")
        self.connection.privmsg(self.CHANNEL, message)
