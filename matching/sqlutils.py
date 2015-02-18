#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
sqlutils
========

"""

import datetime

import sqlalchemy as sqa
from sqlalchemy.sql import select, and_

def get_filtered_ideas(db_info):
    conn_str = makeconnstr(db_info)
#    conn_str = 'sqlite:////home/fhocutt/WMFContractWork/IdeaLab/grantsbot-matching/ideas.db'
    engine = sqa.create_engine(conn_str, echo=True)
    metadata = sqa.MetaData()
    ideas = sqa.Table('idealab_ideas', metadata, autoload=True,
                        autoload_with=engine)
    s = select([ideas.c.idea_title]).where(and_(ideas.c.idea_recent_editors >= 1,
        ideas.c.idea_created > (datetime.datetime.utcnow() - datetime.timedelta(days=90))))
    conn = engine.connect()
    result = conn.execute(s)
    data = result.fetchall()
    return data


def makeconnstr(dbinfo):
    """Return a string with MySQL DB connecting information."""
    username = dbinfo['user']
    password = dbinfo['password']
    host = dbinfo['host']
    dbname = dbinfo['dbname']
    conn_str = 'mysql://{}:{}@{}/{}?charset=utf8&use_unicode=0'.format(
        username, password, host, dbname)
    return conn_str
