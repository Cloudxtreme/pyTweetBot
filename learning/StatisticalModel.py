#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : StatisticalMode.py
# Description : pyTweetBot statistical model for text classification.
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
from .Model import Model, ModelNotFoundException, ModelAlreadyExistsException
from db.obj.Model import Model as DbModel
from db.obj.ModelTokens import ModelToken
import spacy
import pickle
import decimal
from db.DBConnector import DBConnector
from sys import getsizeof
import re


# A statistical model for text classification
class StatisticalModel(Model):
    """
    A statistical model for text classification
    """

    # Constructor
    def __init__(self, features, name, classes, last_update, smoothing, smoothing_param):
        """
        Constructor
        :param name: Model's name
        :param n_classes: Class count
        :param tokens_prob: Array of dictionaries of tokens probabilities
        """
        # Superclass
        super(StatisticalModel, self).__init__(features=features, name=name, classes=classes)

        # Properties
        self._n_token = 0
        self._n_total_token = 0

        # Init dicionaries
        self._token_counters = dict()
        self._class_counters = dict()

        # Smoothing
        self._smoothing = smoothing
        self._smoothing_param = smoothing_param
    # end __init__

    #####################################################
    # Public
    #####################################################

    # Get token count
    def get_token_count(self):
        """
        Get token count
        :return:
        """
        return len(self._token_counters.keys())
    # end get_token_count

    # Train the model
    def train(self, x, y):
        """
        Train the model on a sample
        :param x: Training text
        :param y: Text's class
        """
        # For each token
        for token in x:
            # Token counters
            try:
                self._token_counters[token] += 1.0
            except KeyError:
                self._token_counters[token] = 1.0
                self._n_token += 1.0
            # end try

            # Create entry in class counter
            try:
                probs = self._class_counters[token]
            except KeyError:
                self._class_counters[token] = dict()
            # end try

            # Class counters
            if c in self._class_counters[token].keys():
                self._class_counters[token][y] += 1.0
            else:
                self._class_counters[token][y] = 1.0
            # end if

            # One more token
            self._n_total_token += 1.0
        # end token
    # end train

    ####################################################
    # Override
    ####################################################

    # Get token probability
    def __getitem__(self, item):
        """
        Get token probability
        :param item:
        :return:
        """
        # Probs
        probs = dict()

        # Set default
        for y in self._classes:
            try:
                probs[y] = self._class_counters[item][y] / self._token_counters[item]
            except KeyError:
                probs[y] = 0.0
            # end try
        # end for
        return probs
    # end __getitem__

    # To String
    def __str__(self):
        """
        To string
        :return:
        """
        return "StatisticalModel(name={}, n_classes={}, last_training={}, n_tokens={}, mem_size={}o, " \
               "token_counters_mem_size={} Go, class_counters_mem_size={} Go, n_total_token={})"\
            .format(self._name, self._n_classes,self._last_update, self.get_token_count(),
                    getsizeof(self), round(getsizeof(self._token_counters)/1073741824.0, 4),
                    round(getsizeof(self._class_counters)/1073741824.0, 4), self._n_total_token)
    # end __str__

    # To String
    def __unicode__(self):
        """
        To string
        :return:
        """
        return u"StatisticalModel(name={}, n_classes={}, last_training={}, n_tokens={}, mem_size={}o, " \
               u"token_counters_mem_size={} Go, class_counters_mem_size={} Go, n_total_token={})" \
            .format(self._name, self._n_classes, self._last_update, self.get_token_count(),
                    getsizeof(self), round(getsizeof(self._token_counters) / 1073741824.0, 4),
                    round(getsizeof(self._class_counters) / 1073741824.0, 4), self._n_total_token)
    # end __str__

    ####################################################
    # Private
    ####################################################

    # Prediction
    def _predict(self, x):
        """
        Prediction
        :param x: Sample to classify
        :return: Resulting class number
        """
        # Text's probabilities
        text_probs = dict()

        # Init
        for c in self._classes:
            text_probs[c] = decimal.Decimal(1.0)
        # end for

        # For each token
        for token in x:
            # Get token probs for each class
            try:
                token_probs = self[token]
                collection_prob = self._token_counters[token] / self._n_total_token
            except KeyError:
                continue
            # end try

            # For each class
            for c in self._classes:
                smoothed_value = StatisticalModel.smooth(self._smoothing, token_probs[c], collection_prob, len(x),
                                                         param=self._smoothing_param)
                text_probs[c] *= decimal.Decimal(smoothed_value)
            # end for
        # end for

        # Get highest prob
        max = decimal.Decimal(0.0)
        result_class = ""
        for c in self._classes:
            if text_probs[c] > max:
                max = text_probs[c]
                result_class = c
            # end if
        # end for

        return result_class, text_probs
    # end _predict

    ####################################################
    # Static
    ####################################################

    # Dirichlet prior smoothing function
    @staticmethod
    def smooth_dirichlet_prior(doc_prob, col_prob, doc_length, mu):
        """
        Dirichlet prior smoothing function
        :param doc_prob:
        :param col_prob:
        :param doc_length:
        :param mu:
        :return:
        """
        return (float(doc_length) / (float(doc_length) + float(mu))) * doc_prob + \
               (float(mu) / (float(mu) + float(doc_length))) * col_prob
    # end smooth

    # Jelinek Mercer smoothing function
    @staticmethod
    def smooth_jelinek_mercer(doc_prob, col_prob, param_lambda):
        """
        Jelinek Mercer smoothing function
        :param col_prob:
        :param param_lambda:
        :return:
        """
        return (1.0 - param_lambda) * doc_prob + param_lambda * col_prob
    # end smooth

    # Smoothing function
    @staticmethod
    def smooth(smooth_algo, doc_prob, col_prob, doc_length, param):
        """
        Smoothing function
        :param smooth_algo: Algo type
        :param doc_prob:
        :param col_prob:
        :param doc_length:
        :param param:
        :return:
        """
        if smooth_algo == "dp":
            return StatisticalModel.smooth_dirichlet_prior(doc_prob, col_prob, doc_length, param)
        else:
            return StatisticalModel.smooth_jelinek_mercer(doc_prob, col_prob, param)
        # end if
    # end smooth

# end StatisticalModel
