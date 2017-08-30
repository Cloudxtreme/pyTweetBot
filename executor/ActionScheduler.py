#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : executor/ActionScheduler.py
# Description : Manage bot's actions.
# Auteur : Nils Schaetti <n.schaetti@gmail.com>
# Date : 15.06.2017 18:14:00
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

import sqlalchemy
import datetime
from datetime import timedelta
from db.obj.Action import Action
from db.DBConnector import DBConnector
from twitter.TweetBotConnect import TweetBotConnector
from sqlalchemy import desc
from sqlalchemy import and_
import logging
from patterns.singleton import singleton
import tweet.Tweet as tw
import sys
import time
from threading import Thread


# Reservoir full exception
class ActionReservoirFullError(Exception):
    """
    Reservoir is full
    """
    pass
# end ActionReservoirFullError


# Action already in the DB
class ActionAlreadyExists(Exception):
    """
    The action is already registered in the DB
    """
    pass
# end ActionAlreadyExists


# No factory set
class NoFactory(Exception):
    """
    No factory to create Tweets
    """
    pass
# end NoFactory


# Manage bot's action
@singleton
class ActionScheduler(Thread):
    """
    Manage bot's action
    """

    # Constructor
    def __init__(self, n_actions=None, update_delay=timedelta(minutes=10), reservoir_size=timedelta(days=3),
                 purge_delay=timedelta(weeks=2), config=None, stats=None):
        """
        Constructor
        :param n_exec:
        :param purge_delay:
        """
        # Properties
        self._session = DBConnector().get_session()
        if n_actions == None:
            self._n_actions = {"Follow": 1, "Unfollow": 1, "Like": 1, "Tweet": 1, "Retweet": 1}
        else:
            self._n_actions = n_actions
        # end if
        self._purge_delay = purge_delay
        self._reservoir_size = reservoir_size
        self._update_delay = update_delay
        self._factory = None
        self._config = config

        # Purge the reservoir
        self._purge_reservoir()

        # Thread control and stats
        if config is not None and stats is not None:
            Thread.__init__(self)
            self._stats_manager = stats
        # end if
    # end __init__

    ##############################################
    # Public
    ##############################################

    # Thread running function
    def run(self):
        """
        Thread running function
        :return:
        """
        while True:
            print("run!!")
            # Wait
            scheduler_config = self._config.get_scheduler_config()
            waiting_seconds = self._stats_manager(datetime.datetime.utcnow(), scheduler_config['slope'], scheduler_config['beta'])
            logging.getLogger(u"pyTweetBot").info(u"Waiting {0:.{1}f} minutes for next run".format(waiting_seconds/60.0, 0))
            time.sleep(waiting_seconds)
        # end while
    # end run

    # Add an action to the DB
    def add(self, action):
        """
        Add an action to the DB
        :param action:
        :return:
        """
        # Check that the reservoir is not full
        if not self.full(action.action_type):
            # Add action
            self._session.add(action)

            # Commit
            self._session.commit()
        else:
            raise ActionReservoirFullError(u"To many action in the reservoir to add a new one")
        # end if
    # end add

    # Add a follow action in the DB
    def add_follow(self, friend_id):
        """
        Add a "follow" action in the DB:
        :param friend_id:
        :return:
        """
        self._add_id_action("Follow", friend_id)
    # end add_follow

    # Add an unfollow action in the DB
    def add_unfollow(self, friend_id):
        """
        Add an "unfollow" action in the DB:
        :param friend_id: Twitter account0's ID.
        """
        self._add_id_action("Unfollow", friend_id)
    # end add_unfollow

    # Add a like action in the DB
    def add_like(self, tweet_id):
        """
        Add a "like" action in the DB.
        :param tweet_id: Tweet's ID.
        """
        self._add_id_action("Like", tweet_id)
    # end add_like

    # Add a tweet action in the DB
    def add_tweet(self, tweet):
        """
        Add a tweet action in the DB
        :param tweet: Text of the Tweet or Tweet object.
        """
        if tweet is unicode or tweet is str:
            self._add_text_action("Tweet", tweet)
        elif self._factory is not None:
            self._add_text_action("Tweet", tweet.get_tweet())
        else:
            raise NoFactory(u"No factory given to create Tweets")
        # end if
    # end add_tweet

    # Add a "Retweet" action in the DB
    def add_retweet(self, tweet_id):
        """
        Add a "retweet" action in the DB
        :param tweet_id: Tweet's ID
        """
        self._add_id_action("Retweet", tweet_id)
    # end add_retweet

    # Does an action already exists in the DB?
    def exists(self, action_type, action_tweet_id=None, action_tweet_text=None):
        """
        Does an action already exists in the DB?
        :param action_type: Type of action
        :param action_tweet_id: Tweet's ID (can be None)
        :param action_tweet_text: Tweet's text (can be None)
        :return: True or False
        """
        try:
            if action_tweet_id is None and action_tweet_text is None:
                self._session.query(Action).filter(Action.action_type == action_type).one()
                return True
            elif action_tweet_id is not None and action_tweet_text is None:
                self._session.query(Action).filter(
                    and_(Action.action_type == action_type, Action.action_tweet_id == action_tweet_id)).one()
                return True
            elif action_tweet_id is None and action_tweet_text is not None:
                self._session.query(Action).filter(
                    and_(Action.action_type == action_type, Action.action_tweet_text == action_tweet_text)).one()
                return True
            else:
                self._session.query(Action).filter(
                    and_(Action.action_type == action_type, Action.action_tweet_id == action_tweet_id,
                         Action.action_tweet_text == action_tweet_text)).one()
                return True
            # end if
        except sqlalchemy.orm.exc.NoResultFound:
            return False
        # end try
    # end exists

    # Delete an action
    def delete(self, action):
        """
        Delete an action
        :param action: Action to delete.
        """
        self._session.query(Action).filter(Action.action_id == action.action_id).delete()
        self._session.commit()
    # end delete

    # Execute
    def __call__(self):
        """
        Execute action
        :return:
        """
        # Level per action
        for action_type in ["Follow", "Unfollow", "Like", "Tweet", "Retweet"]:
            # Get actions to be executed
            for action in self._get_exec_action(action_type):
                action.execute()
                self.delete(action)
            # end for
        # end for
    # end __call__

    # Execute next actions
    def exec_next_actions(self):
        """
        Execute next actions
        :return:
        """
        for action_type in ["Follow", "Unfollow", "Like", "Tweet", "Retweet"]:
            # Get action to be executed
            self.exec_next_action(action_type=action_type)
        # end for
    # end exec_next_action

    # Execute next action (by type)
    def exec_next_action(self, action_type):
        """
        Execute next action (by type)
        :param action_type: Action's type (like, follow, etc)
        :return:
        """
        # Get all actions
        action = self._session.query(Action).filter(Action.action_type == action_type) \
            .order_by(Action.action_id).all()[0]
        action.execute()
        self.delete(action)
    # end exec_next_action

    # List actions in the reservoir
    def list_actions(self):
        """
        List actions in the reservoir
        :return:
        """
        # Get actions
        return self._session.query(Action).order_by(Action.action_id).all()
    # end list_actions

    # Is reservoir empty
    def empty(self, action_type):
        """
        Is the reservoir empty?
        :param action_type: Action type
        :return: True or False
        """
        return self._get_reservoir_level(action_type) == 0
    # end if

    # Check if the actions reservoir is full.
    def full(self, action_type):
        """
        Check if the actions reservoir is full for this
        kind of action.
        :param action_type: The kind of action
        :return:
        """
        # Get reservoir level
        reservoir_level = self._get_reservoir_level(action_type)

        # Max number of actions
        max_n_action = int(self._reservoir_size.total_seconds() / self._update_delay.total_seconds()
                           * self._n_actions[action_type])

        # Log
        logging.debug(u"is_reservoir_full: {} in the reservoir for a max value of {}".format(reservoir_level,
                                                                                            max_n_action))

        # reservoir_level >= max_n_action => full
        return reservoir_level >= max_n_action
    # end _is_reservoir_full

    # Get the number of statuses
    def n_statuses(self):
        """
        Get the number of statuses
        :return: The number of statuses
        """
        return TweetBotConnector().get_user().statuses_count
    # end n_statuses

    # Set Tweet factory object
    def set_factory(self, factory):
        """
        Set Tweet factory object
        :param factory:
        :return:
        """
        self._factory = factory
    # end set_factory

    ##############################################
    #
    # Private functions
    #
    ##############################################

    # Purge reservoir
    def _purge_reservoir(self):
        """
        Purge the reservoir of obsolete actions.
        """
        self._session.query(Action).filter(Action.action_date <= datetime.datetime.utcnow() - self._purge_delay)
    # end _purge_reservoir

    # Get reservoir levels
    def _get_reservoir_levels(self):
        """
        Get the number of actions in the reservoir.
        :return: The number of action as a dict()
        """
        result = dict()
        # Level per action
        for action_type in ["Follow", "Unfollow", "Like", "Tweet", "Retweet"]:
            result[action_type] = self._get_reservoir_level(action_type)
        # end for
        return result
    # end _get_reservoir_level

    # Get reservoir level
    def _get_reservoir_level(self, action_type):
        """
        Get the number of action for a action type.
        :param action_type: Action's type.
        :return: Reservoir level for this action
        """
        return len(self._session.query(Action).filter(Action.action_type == action_type).all())
    # end _get_reservoir_level

    # Get action to execute
    def _get_exec_action(self, action_type):
        """
        Get all action to execute
        :return: Action to execute as a list()
        """
        # Get all actions
        exec_actions = self._session.query(Action).filter(Action.action_type == action_type)\
            .order_by(Action.action_id).all()
        return exec_actions[:self._n_actions[action_type]]
    # end _get_exec_action

    # Add action with id
    def _add_id_action(self, action_type, the_id):
        """
        Add action with a id argument.
        :param action_type: Type of action
        :param the_id: Action's ID
        """
        if not self.exists(action_type, the_id):
            action = Action(action_type=action_type, action_tweet_id=the_id)
            self.add(action)
        else:
            logging.getLogger("pyTweetBot").warning(u"{} action for friend/tweet {} already in database"
                                                    .format(action_type, the_id))
            raise ActionAlreadyExists(u"{} action for friend/tweet {} already in database".format(action_type, the_id))
        # end if
    # end _add_id_action

    # Add action with text
    def _add_text_action(self, action_type, the_text):
        """
        Add action with text.
        :param action_type: Type of action
        :param the_text: Action's text.
        """
        if not self.exists(action_type=action_type, action_tweet_text=the_text):
            action = Action(action_type=action_type, action_tweet_text=the_text)
            self.add(action)
        else:
            logging.getLogger("pyTweetBot").warning(u"{} action for text {} already in database"
                                                    .format(action_type, the_text))
            raise ActionAlreadyExists(u"{} action for text {} already in database".format(action_type, the_text))
        # end if
    # end _add_text_action

# end ActionScheduler
