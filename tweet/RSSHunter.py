#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import feedparser
from .Hunter import Hunter
from twitter.TweetGenerator import TweetGenerator
from .Tweet import Tweet


class RSSHunter(Hunter):

    # Constructor
    def __init__(self, stream):
        self._stream = stream
        self._stream_url = stream['url']
        self._entries = feedparser.parse(self._stream_url)['entries']
        self._hashtags = stream['hashtags'] if 'hashtags' in stream else list()
        self._via = stream['via'] if 'via' in stream else None
        self._current = 0
    # end __init__

    # Get stream
    def get_stream(self):
        """
        Get stream
        """
        return self._stream
    # end get_stream

    # Iterator
    def __iter__(self):
        """
        Iterator
        :return:
        """
        return self
    # end __iter__

    # Next
    def next(self):
        """
        Next
        :return:
        """
        if self._current >= len(self._entries):
            raise StopIteration
        # end if
        current_entry = self._entries[self._current]
        self._current += 1

        # Tweet generator
        return Tweet(current_entry['title'], current_entry['links'][0]['href'], self._hashtags, self._via)
    # end next

# end RSSHunter
