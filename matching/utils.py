#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Utility functions for matching.py.
"""

import datetime
import json
import os


def parse_timestamp(t):
    """Parse MediaWiki-style timestamps and return a datetime."""
    if t == '0000-00-00T00:00:00Z':
        return None
    else:
        return datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')


def load_config(filepath):
    configfile = os.path.join(filepath, 'config.json')
    with open(configfile, 'rb') as configf:
        config = json.loads(configf.read())
    return config


def make_category_string(categories):
    return '|'.join(categories)


def timelog(run_time, filepath):
    """Get the timestamp from the last run, then log the current time
    (UTC).
    """
    timelogfile = os.path.join(filepath, 'time.log') # fixme this currently only works because filepath is in the enclosing scope (main)
    try:
        with open(timelogfile, 'r+b') as timelog:
            prevruntimestamp = timelog.read()
            timelog.seek(0)
            timelog.write(datetime.datetime.strftime(run_time,
                                                     '%Y-%m-%dT%H:%M:%SZ'))
            timelog.truncate()
    except IOError:
        with open(timelogfile, 'wb') as timelog:
            prevruntimestamp = ''
            timelog.write(datetime.datetime.strftime(run_time,
                                                     '%Y-%m-%dT%H:%M:%SZ'))
    return prevruntimestamp


def buildgreeting(greeting, username, ideas):
    """Create a customized greeting string to be posted to a talk page
    to introduce a potential mentor to a learner.

    Return the greeting.
    """
    """
        except Exception as e:
            mblog.logerror(u'Could not create a greeting for {}'.format(
                learner['learner']), exc_info=True)
            logged_errors = True
            continue
    """
    idea_string = ''
    for idea in ideas:
        title = idea['profile_title']
        idea_string = '{}* [[{}]]\n'.format(idea_string, title)
    full_greeting = greeting.format(username, idea_string)
    return full_greeting
