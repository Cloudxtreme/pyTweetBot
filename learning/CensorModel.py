#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : CensorModel.py
# Description : pyTweetBot model keeping a list of forbidden words
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

# Imports
import pickle
from .Model import Model


# Forbidden words classifier
class CensorModel(Model):
    """
    Forbidden words
    """

    # Variables
    _finalized = False

    # Constructor
    def __init__(self, config):
        """
        Constructor
        :param config: Settings
        """
        # Forbidden words
        self._forbidden_words = config.get_forbidden_words()
    # end __init__

    #################################################
    # Public
    #################################################

    #################################################
    # Override
    #################################################

    #################################################
    # Private
    #################################################

    # Predict
    def _predict(self, text, lang='en'):
        """
        Predict
        :param text: Text to classify
        :return:
        """

    # end _predict

    #################################################
    # Static
    #################################################

# end Model
