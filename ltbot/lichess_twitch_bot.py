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


LOG = logging.getLogger(f"{__name__}")


class LichessTwitchBot(SingleServerIRCBot):
    def __init__(self, username, owner, client_id, token):
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

    def on_welcome(self, cxn, event):
        for req in ("membership", "tags", "commands"):
            cxn.cap("REQ", f":twitch.tv/{req}")

        cxn.join(self.CHANNEL)
        self.send_message("Now online.")
        LOG.info(f"Connected to twitch channel {self.CHANNEL[1:]}.")

    def on_pubmsg(self, cxn, event):
        tags = {kvpair["key"]: kvpair["value"] for kvpair in event.tags}
        user = {"name": tags["display-name"], "id": tags["user-id"]}
        message = event.arguments[0]

        LOG.info(f"Message from {user['name']}: {message}")

    def send_message(self, message):
        LOG.debug("sending message")
        self.connection.privmsg(self.CHANNEL, message)
