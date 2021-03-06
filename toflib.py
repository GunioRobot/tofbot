# -*- coding: utf-8 -*-
#
# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2011 Etienne Millon <etienne.millon@gmail.com>
#                    Martin Kirchgessner <martin.kirch@gmail.com>
#                    Nicolas Dumazet <nicdumz.commits@gmail.com>
#                    Quentin Sabah <quentin.sabah@gmail.com>
import random
import re
from datetime import datetime, timedelta

# those commands directly trigger cmd_* actions
_simple_dispatch = set()

# those commands directly trigger confcmd_* actions
_simple_conf_dispatch = set()

def cmd(expected_args):
    def deco(func):
        name = func.__name__[4:]
        _simple_dispatch.add(name)
        def f(bot, chan, args):
            if(len(args) == expected_args):
                return func(bot, chan, args)
        f.__doc__ = func.__doc__
        return f
    return deco

def confcmd(expected_args):
    def deco(func):
        name = func.__name__[8:]
        _simple_conf_dispatch.add(name)
        def f(bot, chan, args):
            if(len(args) == expected_args):
                return func(bot, chan, args)
        f.__doc__ = func.__doc__
        return f
    return deco

def sansAccents(string):
    """
    Remplace les accents courants en français par le caractère sans. Ne reconnait que les minuscules !
    """
    result = string.decode("utf-8")
    
    a = re.compile(u"[àâä]")
    result = a.sub("a", result)
    
    e = re.compile(u"é|è|ë|ê")
    result = e.sub("e", result)
    
    u = re.compile(u"[üûù]")
    result = u.sub("u", result)
    
    i = re.compile(u"[ïî]")
    result = i.sub("i", result)
    
    o = re.compile(u"[öô]")
    result = o.sub("o", result)
    
    return result.replace(u"ç", "c")


def distance(string1, string2):
    """
    Levenshtein distance
    http://en.wikibooks.org/wiki/Algorithm_implementation/Strings/Levenshtein_distance#Python
    """
    string1 = ' ' + sansAccents(string1)
    string2 = ' ' + sansAccents(string2)
    dists = {}
    len1 = len(string1)
    len2 = len(string2)
    for i in range(len1):
        dists[i, 0] = i
    for j in range (len2):
        dists[0, j] = j
    for j in range(1, len2):
        for i in range(1, len1):
            if string1[i] == string2[j]:
                dists[i, j] = dists[i-1, j-1]
            else:
                dists[i, j] = min(dists[i-1, j] + 1,
                                  dists[i, j-1] + 1,
                                  dists[i-1, j-1] + 1
                                 )
    return dists[len1-1, len2-1]

class RiddleTeller(object):
    """
    A gentleman (and a scholar) who likes to entertain its audience.
    """

    def __init__(self, riddle, channel, writeback, max_dist):
        self.riddle, self.answer = riddle
        self.channel = channel
        self.writeback = writeback
        self.remaining_msgs = 3
        self.writeback(self.riddle)
        self.max_dist = max_dist

    def wait_answer(self, chan, msg):
        """
        Called at each try.
        Returns True iff the riddle is over.
        """
        if chan != self.channel:
            return False
        if distance(msg.lower(), self.answer.lower()) < self.max_dist:
            self.writeback("10 points pour Griffondor.")
            return True
        self.remaining_msgs -= 1
        if self.remaining_msgs == 0:
            self.writeback(self.answer)
            return True
        return False

class InnocentHand(object):
    """
    A cute 6 years old girl, picking a random object
    from a given pool of candidates
    """
    def __init__(self, pool):
        """
        pool: list of candidates
        """
        self.pool = pool

    def __call__(self, index=None):
        if index:
            return self.pool[index % len(self.pool)]
        random.seed()
        return random.choice(self.pool)

class Plugin(object):

    def __init__(self, bot):
        self.bot = bot

    def say(self, msg):
        self.bot.msg(self.bot.channels[0], msg)

class CronEvent:

    def __init__(self, plugin):
        self.lastTick = datetime.min
        self.period = timedelta(minutes=10)
        self.plugin = plugin

    def fire(self):
        pass

class Cron:
    def __init__(self):
        self.events = []

    def tick(self):
        now = datetime.now ()
        for ev in self.events:
            if now > ev.lastTick + ev.period:
                ev.fire()
                ev.lastTick = now

    def schedule(self, ev):
        self.events.append(ev)
