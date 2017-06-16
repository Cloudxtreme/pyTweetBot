#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : pyTweetBot.py
# Description : pyTweetBot main execution file.
# Auteur : Nils Schaetti <n.schaetti@gmail.com>
# Date : 01.05.2017 17:59:05
# Lieu : Nyon, Suisse
#
# This file is part of the pyTweetBot.
# The pyTweetBot is a set of free software:
# you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyTweetBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with pyTweetBar.  If not, see <http://www.gnu.org/licenses/>.
#

# Import
import argparse
import logging
import datetime
from config.BotConfig import BotConfig
from db.DBConnector import DBConnector
from twitter.TweetBotConnect import TweetBotConnector
from friends.FriendsManager import FriendsManager
from executor.ActionScheduler import ActionScheduler

####################################################
# Main function
####################################################

if __name__ == "__main__":

    # Argument parser
    parser = argparse.ArgumentParser(description="pyTweetBot - Smart Tweeter Bot")

    # Argument
    parser.add_argument("--action", type=str, help="What to do (execute, dm, friends, news, retweet).")
    parser.add_argument("--config", type=str, help="Configuration file", required=True)
    parser.add_argument("--log-level", type=int, help="Log level", default=20)
    args = parser.parse_args()

    # Logging
    logging.basicConfig(level=args.log_level)
    logger = logging.getLogger(name="pyTweetBot")

    # Load configuration file
    config = BotConfig.load(args.config)

    # Connection to MySQL
    dbc = config.get_database_config()
    mysql_connector = DBConnector(host=dbc["host"], username=dbc["username"], password=dbc["password"],
                                  db_name=dbc["database"])

    # Connection to Twitter
    twitter_connector = TweetBotConnector(config)

    # Friends
    friends_manager = FriendsManager()
    #n_follower, d_follower, n_following, d_following = friends_manager.update()
    #logger.info("%d new follower, %d unfollow, %d new following, %d unfollowing")
    """obsolete_friends = friends_manager.get_obsolete_friends(days=14)
    logger.info("Obsolete friends : ")
    for friend in obsolete_friends:
        print(friend.friend_screen_name)
        print(friend.friend_following_date)
    # end for"""

    # Action scheduler
    action_scheduler = ActionScheduler()
    action_scheduler.add_follow(1)

# end if