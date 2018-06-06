#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : find_github_tweets.py
# Description : Tweet information about GitHub activities.
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
import logging
import time

from github import Github

from executor.ActionScheduler import ActionReservoirFullError, ActionAlreadyExists
from tweet.TweetFactory import TweetFactory
from twitter.TweetBotConnect import TweetBotConnector


####################################################
# Globals
####################################################

####################################################
# Functions
####################################################


# Prepare project name
def prepare_project_name(project_name):
    """
    Prepare the project's name
    :param project_name: GitHub project's name
    :return: The project's name prepared
    """
    project_name = project_name.replace(u'-', u' ')
    if u' ' in project_name:
        project_name = project_name.title()
    # end if
    return project_name.replace(u' ', u'')
# end prepare_project_name


# Create tweet text
def create_tweet_text(contrib_counter, contrib_date, project_name, project_url, topics):
    """
    Create tweet's text for push event
    :param contrib_counter: Number of contributions
    :param contrib_date: Date of the push
    :param project_name: GitHub project's name
    :param project_url: GitHub project's URL
    :param topics: GitHub poject's topics
    :return: The created text.
    """
    # Tweet text
    tweet_text = u"I made {} contributions on {} to project #{}, #GitHub".format\
    (
            contrib_counter,
            contrib_date.strftime('%B %d'),
            project_name
    )

    # For each topics
    for topic in topics:
        if len(u"{} #{}".format(tweet_text, topic)) + 21 < 140:
            tweet_text = u"{} #{}".format(tweet_text, topic)
        else:
            break
        # end if
    # end for

    return u"{} {}".format(tweet_text, project_url)
# end create_tweet_text


# Create tweet text for repo creation
def create_tweet_text_create(project_name, project_description, project_url, topics):
    """
    Create tweet text for repo creation
    :param project_name: GitHub project's name
    :param project_description: GitHub project's description
    :param project_url: GitHub project's URL
    :param topics: GitHub project's topics.
    :return: The created text.
    """
    # Tweet text
    tweet_text = u"Check my project {} on #GitHub : {}".format \
    (
        project_name,
        project_description
    )

    # Check Tweet length
    if len(tweet_text) + 21 > 130:
        # Not wanted chars
        overflow_text = 140 - (len(tweet_text) + 21)

        # Remove
        tweet_text = tweet_text[:overflow_text-10] + u"..."
    # end if

    # Add topics
    for topic in topics:
        if len(u"{} #{}".format(tweet_text, topic)) + 21 < 130:
            tweet_text = u"{} #{}".format(tweet_text, topic)
        else:
            break
        # end if
    # end for

    # Return with URL
    return u"{} {}".format(tweet_text, project_url)
# end create_tweet_text_create


# Add tweet to scheduler
def add_tweet(action_scheduler, tweet_text):
    """
    Add tweet to scheduler
    :param action_scheduler: The action scheduler object
    :param tweet_text: Text to tweet
    :return: True if ok, False if problem.
    """
    # Add to scheduler
    try:
        logging.getLogger(u"pyTweetBot").info(u"Adding GitHub Tweet \"{}\" to the scheduler".format(
            tweet_text))
        action_scheduler.add_tweet(tweet_text)
        return True
    except ActionReservoirFullError:
        logging.getLogger(u"pyTweetBot").error(u"Reservoir full for Tweet action, exiting...")
        exit()
        pass
    except ActionAlreadyExists:
        logging.getLogger(u"pyTweetBot").error(
            u"Tweet \"{}\" already exists in the database".format(
                tweet_text.encode('ascii', errors='ignore')))
        return False
    # end try
# end add_tweet


# Tweet something or add it to the database
def compute_tweet(tweet_text, action_scheduler, instantaneous):
    """
    Tweet something or add it to the database.
    :param tweet_text: The text to tweet.
    :param action_scheduler: Action scheduler object
    :param instantaneous: Tweet directly or add it to the DB.
    :return: True if tweeted/added, False otherwise.
    """
    # if not instantaneous
    if not pytweetbot.db.obj.Tweeted.exists(tweet_text):
        if not instantaneous:
            if not add_tweet(action_scheduler, tweet_text):
                return False
            # end if
        else:
            # TODO: Tweeted should be insert in TweetBotConnector.tweet()
            TweetBotConnector().tweet(tweet_text)
            pytweetbot.db.obj.Tweeted().insert_tweet(tweet_text)
        # end if
    else:
        return False
    # end if
    return True
# end compute_tweet


####################################################
# Main function
####################################################

# Add tweets about GitHub activities to the database, or tweet it directly
def find_github_tweets(config, action_scheduler, event_type="push", depth=-1, instantaneous=False, waiting_time=0):
    """
    Add tweets about GitHub activities to the database, or tweet it directly.
    :param config: Bot config object.
    :param action_scheduler: Action scheduler object.
    :param event_type: Type of event to tweet (push or create)
    :param depth: Number of tweets to find.
    :param instantaneous: Tweet the information instantaneously or not (to DB)?
    :param waiting_time: Waiting time between each tweets (for instantaneous tweeting)
    """
    # Github settings
    github_settings = config.github

    # Login info
    login = github_settings['login']
    password = github_settings['password']
    exclude = github_settings['exclude']
    topics = github_settings['topics']

    # Connection
    g = Github(login, password)

    # For each repositories
    for repo in g.get_user().get_repos():
        # No private repositories
        if not repo.private and repo.name not in exclude:
            # Project's name
            project_name = prepare_project_name(repo.name)
            project_url = u"https://github.com/{}/{}".format(login, project_name, repo.name)
            project_description = repo.description

            # Topics
            if repo.name in topics:
                project_topics = topics[repo.name]
            else:
                project_topics = []
            # end if

            # Counter and date
            contrib_counter = 0
            contrib_date = None
            tweet_count = 0

            # For each events
            for event in repo.get_events():
                # Only pushes
                if event.type == u"PushEvent" and event_type == "push":
                    # Same day?
                    if contrib_date is not None and event.created_at.year == contrib_date.year and event.created_at.month == contrib_date.month and event.created_at.day == contrib_date.day:
                        contrib_counter += 1
                    else:
                        # Something to tweet?
                        if contrib_date is not None:
                            # Tweet text
                            tweet_text = create_tweet_text(contrib_counter, contrib_date, project_name, project_url, project_topics)

                            # Compute
                            if not compute_tweet(tweet_text, action_scheduler, instantaneous):
                                break
                            # end if

                            # Waiting time
                            if waiting_time > 0:
                                time.sleep(waiting_time)
                            # end if

                            # Check depth
                            tweet_count += 1
                            if depth != -1 and tweet_count >= depth:
                                break
                            # end if
                        # end if

                        # Reset counter and date
                        contrib_counter = event.payload['size']
                        contrib_date = event.created_at
                elif event.type == u"CreateEvent" and event_type == "create" and event.payload['ref_type'] == u"repository":
                    # Tweet text
                    tweet_text = TweetFactory()(create_tweet_text_create(project_name, project_description, project_url, project_topics))

                    # Compute
                    compute_tweet(tweet_text, action_scheduler, instantaneous)

                    # Waiting time
                    if waiting_time > 0:
                        time.sleep(waiting_time)
                    # end if
                # end if
            # end for
        # end if
    # end for

# end if
