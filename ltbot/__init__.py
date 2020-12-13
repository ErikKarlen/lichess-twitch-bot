"""Lichess Twitch Bot Module

This module contains classes and functions for using a Twitch bot and
Lichess bot for playing chess on Lichess with Twitch chat.

    * LichessTwitchBot - Bot for playing on Lichess with Twitch chat
    * LTBotManager - Manages Lichess Twitch bot
    * load_configuration - Loads bot configuration from yaml file
    * setup_logging - Enables logging for program

    COPYRIGHT INFORMATION
    ---------------------
Based on the twitch bot tutorial by Carberra.
    https://github.com/Carberra/twitch-bot-tutorial/blob/master/twitch_tut.py
Some code in this file is licensed under the Apache License, Version 2.0.
    http://aws.amazon.com/apache2.0/
"""

from .lichess import Lichess
from .lichess_twitch_bot import LichessTwitchBot
from .ltbot_manager import LTBotManager
from .util import load_configuration, setup_logging
