#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : twitter.PyTweetBotConnector.py
# Description : pyTweetBot Twitter connector.
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

import tweepy


# Twitter connector
class PyTweetBotConnector(object):
    """
    Twitter Connector
    """

    # Constructor
    def __init__(self, auth_token1, auth_token2, access_token1, access_token2):
        """
        Constructor
        :param auth_token1: Twitter first auth token.
        :param auth_token2: Twitter second auth token.
        :param access_token1: Twitter first access token.
        :param access_token2: Twitter second access token.
        """
        # Auth to Twitter
        auth = tweepy.OAuthHandler(auth_token1, auth_token2)
        auth.set_access_token(access_token1, access_token2)
        self._api = tweepy.API(auth)
    # end __init__

    # Retweet
    def retweet(self, tweet_id):
        """
        Retweet
        :param tweet_id: Tweet's ID.
        """
        self._api.retweet(tweet_id)
    # end retweet

    # Tweet
    def tweet(self, text):
        """
        Send a Tweet
        :param text: Tweet's text.
        """
        self._api.update_status(status=text)
    # end tweet

    # Unfollow
    def unfollow(self, user_id):
        """
        Unfollow
        :param user_id: Twitter user's ID to follow.
        """
        self._api.destroy_friendship(user_id)
    # end unfollow

    # Follow
    def follow(self, user_id):
        """
        Follow a user.
        :param user_id:
        """
        self._api.create_friendship(user_id)
    # end follow

    # Like
    def like(self, tweet_id):
        """
        Like a tweet.
        :param tweet_id: Tweet's ID.
        """
        self._api.create_favorite(tweet_id)
    # end like

    # Send direct message
    def send_direct_message(self, user_id, text):
        """
        Send direct message.
        :param user_id: Receipe user's ID.
        :param text: Message's text.
        """
        self._api.send_direct_message(user_id=user_id, text=text)
    # end send_direct_message

    # Get timeline
    def get_timeline(self, n_pages):
        c = tweepy.Cursor(self._api.home_timeline).pages(limit=n_pages)

# end PyTweetBotConnector
