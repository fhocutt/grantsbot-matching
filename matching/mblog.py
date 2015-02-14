#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
mblog
~~~~

This module contains logging functions for MatchBot. These can log
errors and run history to text files and matches to a relational
database.
"""

import logging
import logging.handlers
import sys
import os

import sqlalchemy as sqa

import sqlutils
from load_config import config, filepath

# possibly hacky
logpath = os.path.join(filepath, 'log')


def logrun(run_time, edited_pages, wrote_db, logged_errors):
    """Log information for each run to external log files.

    Parameters:
        run_time        :   Time that the script starts running
        edited_pages    :   True if any pages were edited
        wrote_db        :   True if the DB was modified at least once
        logged_errors   :   True if any errors were logged

    Example output in log file:
        INFO    2015-01-01 01:00:45.650401      Edited: False   Wrote DB: False Errors: False

    Rotating logs will each be used for 30 d. Two backup logs are kept.
    """
    message = '{0}\tEdited: {1}\tWrote DB: {2}\tErrors: {3}'.format(
        run_time, edited_pages, wrote_db, logged_errors)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s\t%(message)s')
    handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(logpath, 'matchbot.log'), when='D', interval=30,
        backupCount=2, utc=True)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info(message)


# TODO: add some sort of automatic error notification, possibly
# a post on a wikipage
def logerror(message, exc_info=False):
    """Log information when an error occurs to an external log file.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(os.path.join(logpath, 'matchbot_errors.log'))
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.error(message, exc_info=exc_info)


def logmatch(match_info):
    """Log information about the match to a relational database.

    Parameters:
        luid        :   int. Learner's userid.
        lprofile    :   int. Pageid for the learner's profile.
        category    :   string. Category from the learner's profile that
                        they were matched on.
        muid        :   int. Mentor's userid.
        matchtime   :   datetime. Time the match was posted on learner's
                        profile talk page.
        cataddtime  :   datetime. Time the category was added to the
                        learner's profile page.
        matchmade   :   boolean. True if a specific mentor was found
        run_time    :   datetime. time the script started running
        revid       :   int. If not a Flow board, the new revid after
                        posting the new match.
        postid      :   int. If a Flow board, the post-revision-id after
                        posting the new topic for the match.
    """
#    conn_str = sqlutils.makeconnstr(dbinfo, matches)
    conn_str = 'sqlite:////home/fhocutt/WMFContractWork/IdeaLab/grantsbot-matching/matches.db'
    engine = sqa.create_engine(conn_str, echo=True)
    metadata = sqa.MetaData()
    matches = sqa.Table('matches', metadata, autoload=True,
                        autoload_with=engine)
    ins = matches.insert()
    conn = engine.connect()
    conn.execute(ins, match_info)
