#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
matching
~~~~~~~~
Look at me. I am a docstring.

This is an early draft of the matching script for GrantsBot.
"""

import datetime
import sys
import os

import mwclient

import mbapi
import mblog
from load_config import filepath, config

optoutcat = config['categories']['optout']
personcategories = config['categories']['personcats']
ideacategories = config['categories']['ideacats']

def parse_timestamp(t):
    """Parse MediaWiki-style timestamps and return a datetime."""
    if t == '0000-00-00T00:00:00Z':
        return None
    else:
        return datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')

#TODO: check on mbapi.getnewmembers, getallcatmembers, mblog.logerror
def getprofiles(prevruntimestamp, site)
    """
    Returns a dict of profiles.
    """
    optedoutprofiles = mbapi.getallcatmembers(optoutcat, site)
    for category in personcategories:
        try:
            newprofiles = mbapi.getnewmembers(category, site,
                                              prevruntimestamp)
            # this deduplicates (via overwriting but that's ok) as well as checking it's in the IdeaLab
            profiles = {x['profiletitle']: x for x in newprofiles
                        if x['profiletitle'].startswith(prefix)
                        and x['profiletitle'] not in optedoutprofiles}
        except Exception as e:
            mblog.logerror('Could not fetch new profiles in {}'.format(
                category), exc_info=True)
            logged_errors = True
    return profiles


# figure out *something* about mbapi; have it return the desired information
def getprofileinfo(profiles, site):
    # some sort of call to mbapi to fill out the profile dicts
    for profile in profiles:
        x, y, z = mbapi.getxyz(profile, site)
        profile[x], profile[y], profile[z] = x, y, z
    # handle errors here per getlearnerinfo
    return profiles


def getideas(ideas, skill, topic, site):
    # where do I filter on?
    # also lazy-load ideas[topic][skill];
    if topic in ideas and skill in ideas[topic]:
        return ideas[topic][skill]
    else:
        ideacat = ideacategories[topic][skill]
        ideas[topic][skill] = mbapi.getideas(ideacat, site)
        return ideas[topic][skill]


def getideainfo(ideas, site):
    # fill out the idea dicts; this could also work on a single idea just fine
    for idea in ideas:
        x, y, z = mbapi.getxyz(profile, site)
        profile[x], profile[y], profile[z] = x, y, z
    # handle errors here per getlearnerinfo
    return ideas


# TODO: figure out how to make a list sorted on a parameter from a list of dicts
# OR decide to get the API to sort for us and not need this
def chooseideas(idealist):
    # given ideas choose the "best" ones according to criteria and also magic
    pass


def buildgreeting(username, skill, topic, ideas):
    """Create a customized greeting string to be posted to a talk page
    to introduce a potential mentor to a learner.

    Return the greeting and a topic string for the greeting post.
    """
    greetings = config['greetings']
    if skill and topic:
        greeting = greetings['twomatchgreeting'].format(topic, skill) #FIXME in config
        topic = greetings['twomatchtopic']
    elif skill:
        greeting = greetings['onematchgreeting'].format(skill)
        topic = greetings['onematchtopic']
    elif topic:
        greeting = greetings['onematchgreeting'].format(topic)
        topic = greetings['onematchtopic']
    else:
        greeting = greetings['defaultgreeting'].format(username, ideas)
        topic = greetings['defaulttopic']
    return (greeting, topic)


def getprofiletalkpage(profile):
    """Get the talk page for a profile (a sub-page of the Co-op)."""
    talkpage = talkprefix + profile.lstrip(prefix)
    return talkpage


def postinvite(pagetitle, greeting, topic, username, site):
    profile = site.Pages[pagetitle]
    addedtext = config['greetings']['template'].format(topic,
        learner, greeting)
    newpagecontents = '{0} {1}'.format(profile.text(), addedtext)
    result = profile.save(newpagecontents, summary=topic)
    return result


def main():
    # Get last time run, save time of run to log
    try:
        prevruntimestamp = timelog(run_time)
    except Exception as e:
        mblog.logerror(u'Could not get time of previous run', exc_info=True)
        logged_errors = True
        sys.exit()

    # Initializing site + logging in
    login = config['login']
    try:
        site = mwclient.Site((login['protocol'], login['site']),
                              clients_useragent=login['useragent'])
        site.login(login['username'], login['password'])

    except mwclient.LoginError as e:
        mblog.logerror(u'Login failed for {}'.format(login['username']),
                       exc_info=True)
        logged_errors = True
        sys.exit()

# fetch new profiles:
# list of profiles; relevant information about them?
# TODO what's relevant?
    newprofiles = getprofileinfo(getprofiles(prevruntimestamp, site), site)
    """ Profile structure:
    {profiletitle: {'username': , 'userid': , 'skill': , 'interest': , 'profiletitle': , 'profileid': , 'profiletalktitle': }, ... }
    """


# get all the ideas (ALL THE IDEAS)
# get information about all the ideas (anything that you'd need to match on)
# if this makes it slow, can optimize later
# TODO: figure out how to store this, if needed?
# ok--or could only fetch as needed (most active/newest as fallback; fetch by skill or interest (fallback); fetch by skill-and-interest (try this first))

# get a bunch of information about the ideas (activity, how recent; basically, anything I might want to filter on)
    ideas = {}
# load info for default ideas? maybe not, actually
    ideas = getideainfo(getideas(ideas, None, None, site)

    """
    ideas = {topic:
                {skill1:
                    [{title: , lastedited: datetime, ??? (activity level numbers here?, anything needed for selecting ideas)}, ... ],
                 skill2: [...]},
             topic2:
                {skill1: [],
                 skill2: []}
            }


    """

    for profile in newprofiles:

        skill = profile[skill]
        topic = profile[topic]

        # get a set of ideas (match)
        idealist = getideas(ideas, skill, topic, site)

        if idealist is []:
            idealist = getideas(ideas, None, topic, site)
        if idealist is []:
            ideas = getideas(ideas, None, None, site)

        # lazy loading of ideas. check if skill is in ideas[topic] and if not, load; if it is (even if falsy) it has been checked
        # fetch all relevant ideas
        # get matches from ideas fetched
        finalideas = chooseideas(idealist)

        try:
            greeting, topic = buildgreeting(profile['username'], etc. and so forth, topic, skill, FIXME)

        except Exception as e:
            mblog.logerror(u'Could not create a greeting for {}'.format(
                learner['learner']), exc_info=True)
            logged_errors = True
            continue

#noflow
        try:
            response = postinvite(talkpage, greeting, topic, skill, person)
            edited_pages = True
        except Exception as e:
            mblog.logerror(u'Could not post match on {}\'s page'.format(
                profile['username']), exc_info=True)
            logged_errors = True
            continue

# fix up all of this for new things and new db schema
        try:
            revid, matchtime = response['revid'], response['timeposted'] #or whatever
            #needed?
            cataddtime = parse_timestamp(learner['cattime'])
            mblog.logmatch(luid=learner['luid'], lprofileid=learner['profileid'],
                           muid=muid, category=skill, cataddtime=cataddtime,
                           matchtime=matchtime, matchmade=matchmade,
                           revid=revid, postid=postid, run_time=run_time)
            wrote_db = True
        except Exception as e:
            mblog.logerror(u'Could not write to DB for {}'.format(
                learner['learner']), exc_info=True)
            logged_errors = True
            continue

    try:
        mblog.logrun(run_time, edited_pages, wrote_db, logged_errors)
    except Exception as e:
        mblog.logerror(u'Could not log run at {}'.format(run_time),
            exc_info=True)


if __name__ == '__main__':
    main()
