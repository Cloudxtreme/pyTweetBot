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
import logging
import threading
from Queue import Queue
from config.BotConfig import BotConfig
from executor.ExecutorThread import ExecutorThread

####################################################
# Main function
####################################################


# Execute actions
def execute_actions(action_scheduler):
    """
    Execute actions
    :param action_scheduler:
    :param action_type:
    """
    # List of threads
    thread_queue = Queue()

    # For each action type
    for action_type in action_scheduler.action_types:
        # New executor thread
        executor_thread = ExecutorThread(BotConfig(), action_scheduler, action_type)

        # Start executing action
        logging.getLogger(u"pyTweetBot").info(u"Start thread for action type {}...".format(action_type))

        # Start as daemon
        executor_thread.daemon = True
        executor_thread.start()

        # Add to queue
        thread_queue.put(executor_thread)
    # end for

    # Waiting for the thread to terminate
    try:
        thread_queue.join()
    except (KeyboardInterrupt, SystemExit):
        logging.getLogger(u"pyTweetBot").info(u"Stopping executing action with scheduler...")
    # end try
# end execute_actions
