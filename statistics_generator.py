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
import time
import numpy as np
import matplotlib.pyplot as plt
from twitter.TweetBotConnect import TweetBotConnector
from db.obj.ImpactStatistics import ImpactStatistic
from config.BotConfig import BotConfig
from db.DBConnector import DBConnector

####################################################
# Main function
####################################################

if __name__ == "__main__":

    # Argument parser
    parser = argparse.ArgumentParser(description="pyTweetBot - Smart Tweeter Bot")

    # Argument
    parser.add_argument("--config", type=str, help="Configuration file", required=True)
    parser.add_argument("--log-level", type=int, help="Log level", default=20)
    parser.add_argument("--n-pages", type=int, help="Number of page to take into account", default=-1)
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

    # Stats for each day of the week
    week_day_stats = np.zeros((7, 24))
    week_to_string = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # For each of my tweets
    for index, page in enumerate(twitter_connector.get_user_timeline(screen_name="nschaetti", n_pages=args.n_pages)):
        logging.info(u"Analyzing page number {}".format(index))

        # For each tweet
        for tweet in page:
            if not tweet.retweeted:
                week_day_stats[tweet.created_at.weekday(), tweet.created_at.hour] += 1
            # end if
        # end for

        # Update DB
        for week_day in range(7):
            for hour in range(24):
                count = week_day_stats[week_day, hour]
                the_week_day = week_to_string[week_day]
                if ImpactStatistic.exists(the_week_day, hour):
                    ImpactStatistic.update(the_week_day, hour, count)
                else:
                    impact_stat = ImpactStatistic(impact_statistic_week_day=the_week_day,
                                                  impact_statistic_hour=hour,
                                                  impact_statistic_count=count)
                    DBConnector().get_session().add(impact_stat)
                # end if
            # end for
        # end for

        # Commit
        DBConnector().get_session().commit()

        # Wait
        time.sleep(60)
    # end for

# end if
