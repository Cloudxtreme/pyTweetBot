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
import nsNLP
import logging
import os
import sys
import urllib
from bs4 import BeautifulSoup
from learning.Model import Model
from learning.Dataset import Dataset


####################################################
# Functions
####################################################


####################################################
# Main function
####################################################


# Test a classifier
def model_testing(data_set_file, model_file, features='words'):
    """
    Test a classifier
    :param data_set_file: Path to the dataset file
    :param model_file: Path to model file if needed
    :param features: Features
    """
    # Load model or create
    if os.path.exists(model_file):
        model = nsNLP.classifiers.TextClassifier.load(model_file)
    else:
        sys.stderr.write(u"Can't open model file {}\n".format(model_file))
        exit()
    # end if

    # Load data set
    if os.path.exists(data_set_file):
        dataset = Dataset.load(data_set_file)
    else:
        logging.error(u"Cannot find dataset file {}".format(data_set_file))
    # end if

    # Tokenizer
    tokenizer = nsNLP.tokenization.NLTKTokenizer(lang='english')

    # Parse features
    feature_list = features.split('+')

    # Join features
    bow = nsNLP.features.BagOfGrams()

    # For each features
    for bag in feature_list:
        # Select features
        if bag == 'words':
            b = nsNLP.features.BagOfWords()
        elif bag == 'bigrams':
            b = nsNLP.features.BagOf2Grams()
        elif bag == 'trigrams':
            b = nsNLP.features.BagOf3Grams()
        else:
            sys.stderr.write(u"Unknown features type {}".format(features))
            exit()
        # end if
        bow.add(b)
    # end for

    # Stats
    confusion_matrix = {'pos': {'pos': 0.0, 'neg': 0.0}, 'neg': {'pos': 0.0, 'neg': 0.0}}

    # Higher false positive probs
    higher_pos_prob = 0.0
    higher_pos_text = ""

    # Print model
    print(u"Using model {}".format(model))

    # For each URL in the dataset
    index = 1
    for text, c in dataset:
        # Log
        print(u"Testing sample {}/{}".format(index, len(dataset)))

        # Predict
        prediction, probs = model(bow(tokenizer(text)))

        # Save result
        confusion_matrix[prediction][c] += 1.0

        # Compare
        print(u"Predicted {} for observation {}".format(prediction, c))

        # Show false positive
        if prediction == 'pos' and c == 'neg':
            #print(text)
            if probs['pos'] > higher_pos_prob:
                higher_pos_prob = probs['pos']
                higher_pos_text = text
            # end if
        # end if

        # Index
        index += 1
    # end for

    # False positive/negative
    false_positive = confusion_matrix['pos']['neg'] / float(len(dataset))
    false_negative = confusion_matrix['neg']['pos'] / float(len(dataset))
    success_rate = (confusion_matrix['pos']['pos'] + confusion_matrix['neg']['neg']) / float(len(dataset))

    # Show performance
    print\
    (
        u"Success rate of {} on dataset, {} false positive, {} false negative"
            .format(success_rate*100.0, false_positive*100.0, false_negative*100.0)
    )

    # Show prob stats
    print(u"Higher 'positive' probability for a false positive is {}".format(higher_false_prob))
    print(u"for the text {}".format(higher_false_text))

# end if
