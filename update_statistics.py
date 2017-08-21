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
from config.BotConfig import BotConfig
from db.DBConnector import DBConnector
from stats.UserStatistics import UserStatistics
from twitter.TweetBotConnect import TweetBotConnector
from mail.MailBuilder import MailBuilder
from mail.MailSender import MailSender
import pkg_resources


####################################################
# Main function
####################################################

if __name__ == "__main__":

    # Argument parser
    parser = argparse.ArgumentParser(description="pyTweetBot - Smart Tweeter Bot")

    # Argument
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

    # Get last statistics
    last_stats = UserStatistics().get_last_statistics()

    # Update statistics in the DB
    n_followers, n_following, n_statuses = UserStatistics().update_statistics()

    # Get template
    template = pkg_resources.resource_string("templates", 'weekly_statistics.html')

    # Mail builder
    mail_builder = MailBuilder(template)

    # Last report date
    mail_builder['date_last'] = unicode(last_stats.statistic_date)

    # Parameter template
    mail_builder['followers'] = n_followers
    mail_builder['following'] = n_following
    mail_builder['statuses'] = n_statuses

    # Differences
    mail_builder['diff_followers'] = (n_followers - last_stats.statistic_followers_count)
    mail_builder['diff_following'] = (n_following - last_stats.statistic_friends_count)
    mail_builder['diff_statuses'] = (n_statuses - last_stats.statistic_statuses_count)

    # Mail
    to_address = config.get_email()

    # Mail sender
    sender = MailSender(subject="Your weekly update", from_address="pytweetbot@bot.ai", to_addresses=[to_address],
                        msg=mail_builder.message())

    # Send
    sender.send()
# end if
