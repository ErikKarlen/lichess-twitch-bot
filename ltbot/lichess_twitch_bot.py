import collections
import enum
import logging
import threading

from requests import get
from irc.bot import SingleServerIRCBot
from irc.client import ServerConnection, Event

from . import Lichess


LOG = logging.getLogger(__name__)


class BotState(enum.Enum):
    IDLE = 0
    CHALLENGE_VOTE = 1
    WAIT_FOR_OPPONENT = 2
    PLAY_MOVE = 3


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

        self.challenge_vote_time = configuration["challenge_vote_time"]

        self.challenge_parameters_command = configuration["command"]["challenge_parameters"]
        self.challenge_start_command = configuration["command"]["challenge_start"]
        self.challenge_vote_command = "{} ".format(configuration["command"]["challenge_vote"])
        self.clock_limit_command = "{} ".format(configuration["command"]["clock_limit"])
        self.clock_increment_command = "{} ".format(configuration["command"]["clock_increment"])

        self.clock_limit_limits = (60, 10800)
        self.clock_increment_limits = (0, 60)
        self.clock_limit = configuration["lichess"]["initial_clock_limit"]
        self.clock_increment = configuration["lichess"]["initial_clock_increment"]

        self.vote_dict = {}
        self.bot_state = BotState.IDLE

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

        if self.bot_state == BotState.IDLE:
            self.idle_handle_message(user["name"], message)
        elif self.bot_state == BotState.CHALLENGE_VOTE:
            self.challenge_vote_handle_message(user["name"], message)

        LOG.info(f"Message from {user['name']}: {message}")

    def idle_handle_message(self, user: str, message: str):
        """Handles the incoming message when idling.

        Parameters
        ----------
        user : str
            The sender of the message
        message : str
            The user's message
        """

        if message == self.challenge_start_command:
            self.bot_state = BotState.CHALLENGE_VOTE
            LOG.debug("Starting Lichess challenge vote.")
            self.challenge_vote_start()
        elif message.startswith(self.clock_limit_command):
            self.clock_limit_handle_message(message)
        elif message.startswith(self.clock_increment_command):
            self.handle_clock_limit_request(message)
        elif message == self.challenge_parameters_command:
            LOG.info("Challenge parameters requested from user {}".format(user))
            self.send_message(
                "@{} Clock limit: {}, Clock increment: {}".format(
                    user, self.clock_limit, self.clock_increment
                )
            )

    def challenge_vote_start(self):
        """Starts a vote for who to challenge on Lichess

        Starts a vote in Twitch chat for who to challenge on Lichess by resetting the
        votes dictionary, updating the bot state and starting a timer. Announces in
        Twitch chat that a vote has started.
        """

        self.vote_dict = {}
        self.bot_state = BotState.CHALLENGE_VOTE
        threading.Timer(self.challenge_vote_time, self.challenge_vote_finish).start()
        LOG.info("Started vote for who to challenge on Lichess.")
        self.send_message(
            "Starting a vote for who to challenge on Lichess. "
            "Type {}<lichess username> to vote.".format(self.challenge_vote_command)
        )

    def challenge_vote_handle_message(self, user: str, message: str):
        """Handles the incoming message when voting for who to challenge on Lichess

        Parameters
        ----------
        user : str
            The sender of the message
        message : str
            The user's message
        """

        if len(message) > len(self.challenge_vote_command) and message.startswith(
            self.challenge_vote_command
        ):
            vote = message[len(self.challenge_vote_command) :]
            if user in self.vote_dict:
                self.vote_dict[user] = vote
                LOG.info("User {} changed their vote to {}.".format(user, vote))
            else:
                self.vote_dict[user] = vote
                LOG.info("User {} voted for {}.".format(user, vote))

    def challenge_vote_finish(self):
        """Ends the vote for who to challenge on Lichess

        Stops accepting votes for who to challenge and finds out who won. Announces the
        results in Twitch chat.
        """
        LOG.info("Challenge vote finished.")
        if len(self.vote_dict) > 0:
            winner, count = collections.Counter(self.vote_dict.values()).most_common(1)[0]
            LOG.info("Winner is {} with {} vote(s).".format(winner, count))
            self.bot_state = BotState.WAIT_FOR_OPPONENT
            self.lichess_bot.create_challenge(winner, self.clock_limit, self.clock_increment)
            self.send_message(
                "Challenged {} to a game on Lichess, waiting for answer.".format(winner)
            )
        else:
            self.bot_state = BotState.IDLE
            LOG.info("No votes for who to challenge, bot will idle.")
            self.send_message(
                "No votes were registered, type {} to start a new vote.".format(
                    self.challenge_start_command
                )
            )

    def clock_limit_handle_request(self, message: str):
        """Handles the request to update the clock limit

        Parameters
        ----------
        message : str
            The user's message
        """
        try:
            new_clock_limit = int(message[len(self.clock_limit_command) :])
            print(new_clock_limit)
            if (
                self.clock_limit_limits[0] <= new_clock_limit
                and new_clock_limit <= self.clock_limit_limits[1]
                and new_clock_limit % 60 == 0
            ):
                self.clock_limit = new_clock_limit
                LOG.info("Set new clock limit to {}.".format(self.clock_limit))
                self.send_message("New clock limit set to {}.".format(self.clock_limit))
            else:
                LOG.info("Clock limit outside limits.")
                self.send_message(
                    "Couldn't update clock limit, make sure the new value is between {} and {}.".format(
                        self.clock_limit_limits[0], self.clock_limit_limits[1]
                    )
                    + " Also make sure it is divisible by 60."
                )
        except:
            LOG.exception("Failed to update clock limit.")
            self.send_message(
                "Failed to update clock limit, did you use the command correctly? "
                "It should be {}<new clock limit>".format(self.clock_limit_command)
            )
    
    def clock_increment_handle_request(self, message: str):
        """Handles the request to update the clock increment

        Parameters
        ----------
        message : str
            The user's message
        """
        try:
            new_clock_increment = int(message[len(self.clock_increment_command) :])
            if (
                self.clock_increment_limits[0] <= new_clock_increment
                and new_clock_increment <= self.clock_increment_limits[1]
            ):
                self.clock_increment = new_clock_increment
                LOG.info("Set new clock increment to {}.".format(self.clock_increment))
                self.send_message("New clock increment set to {}.".format(self.clock_increment))
            else:
                LOG.info("Given clock increment outside limits.")
                self.send_message(
                    "Couldn't update clock increment, make sure the new value is between {} and {}.".format(
                        self.clock_increment_limits[0], self.clock_increment_limits[1]
                    )
                )
        except:
            LOG.exception("Failed to update clock increment.")
            self.send_message(
                "Failed to update clock increment, did you use the command correctly? "
                "It should be {}<new clock increment>".format(self.clock_increment_command)
            )

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
