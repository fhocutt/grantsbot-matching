#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Utility functions for matching.py.
"""

import datetime
import json
import os
import mbapi

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


def get_profile_talk_page(profile, talk_id, site):
    """Get the talk page for a profile (a sub-page of the Co-op)."""
    if talk_id:
        talkpage = mbapi.get_page_title(talk_id, site)
    else:
        talkpage = talkprefix + profile.lstrip(prefix) #FIXME avoid globals
    return talkpage

