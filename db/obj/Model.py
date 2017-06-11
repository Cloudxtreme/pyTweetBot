#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : Friend.py
# Description : pyTweetBot statistic class in the DB.
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
import datetime
from sqlalchemy import Column, BigInteger, String, DateTime
from .Base import Base
from sqlalchemy.types import Enum


# Model description
class Model(Base):
    """
    Model description
    """

    # Table name
    __tablename__ = "pytwb_models"

    # Fields
    model_id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    model_type = Column(Enum('Tweet', 'Retweet', 'Follow', 'Message'), nullable=False)
    model_last_update = Column(DateTime, nullable=False, default=datetime.datetime.now())

# end Statistic
