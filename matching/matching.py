#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
matching
~~~~~~~~
Look at me. I am a docstring.

This is an early draft of the matching script for GrantsBot.
"""

import datetime
import json
import sys
import os
import random

import mwclient

import mbapi
import mblog
import utils
import sqlutils


def login(creds):
    # Initializing site + logging in
    try:
        site = mwclient.Site((creds['protocol'], creds['site']),
                              clients_useragent=creds['useragent'])
        site.login(creds['username'], creds['password'])
        return site
    except mwclient.LoginError as e:
        mblog.logerror(u'Login failed for {}'.format(creds['username']),
                       exc_info=True)
        logged_errors = True
        sys.exit()


def get_profiles(prev_run_timestamp, categories, site):
    """
    Returns a dict of profiles.
    """
    opted_out_profiles = mbapi.get_all_category_members(categories['people']['optout'], site)
    all_categories = categories['people']['skills'] + categories['people']['topics']
    new_profiles = []
    for category in all_categories:
        new_profiles = new_profiles + mbapi.get_new_members(category, site, prev_run_timestamp)
    return (new_profiles, opted_out_profiles)


def filter_profiles(new_profiles, opted_out_profiles, prefix):
    """makes a dict of profile dicts. In the process, filters
    out opted-out profiles and profiles not in the IdeaLab.
    """
    opted_out_titles = [x['profile_title'] for x in opted_out_profiles]
    profiles = {x['profile_title']: x for x in new_profiles
                if x['profile_title'].startswith(prefix)
                and x['profile_title'] not in opted_out_titles}
    return profiles


def get_profile_info(profiles, categories, prefixes, site):
    """ Profile structure:
    {profiletitle: {'username': , 'userid': , 'skills': [], 'interests': [], 'profiletitle': , 'profileid': , 'profiletalktitle': }, ... }
    """
    for profile in profiles:
        personcats = (categories['people']['skills']
            + categories['people']['topics'])

        page_info = mbapi.get_page_info(profile, personcats, site)
        print(page_info)
        username, userid, talk_id, page_categories = page_info

        # FIXME: could probably refactor this
        profile_dict = profiles[profile]
        profile_dict['username'], profile_dict['userid'] = username, userid
        profile_dict['talk_id'] = talk_id
        profile_dict['talk_title'] = get_profile_talk_page(profile, talk_id,
                                                           prefixes, site)
        profile_dict['skills'], profile_dict['interests'] = [], []

        # we've only retrieved skills and interests, now we see which
        # is which and save it
        for category in page_categories:
            if category['title'] in categories['people']['skills']:
                profile_dict['skills'].append(category['title'])
            else:
                pass

            if category['title'] in categories['people']['topics']:
                profile_dict['interests'].append(category['title'])
            else:
                pass
    # TODO: handle errors here per matchbot.getlearnerinfo()
    return profiles


# there's something weird here; it was deleting a slash, make as robust as possible
def get_profile_talk_page(profile, talk_id, prefixes, site):
    # pretty sure you can do something with site.namespaces; maybe?
    """Get the talk page for a profile (a sub-page of the IdeaLab)."""
    if talk_id:
        talkpage = mbapi.get_page_title(talk_id, site)
    else:
        talkpage = prefixes['talk'] + profile.lstrip(prefixes['main'])
    return talkpage


def get_active_ideas(run_time, config):
    """ Checks the idea database for active ideas. Also does some string
    formatting to get them in the same form as the API returns them.
    """
    return [u'Grants:{}'.format(x[0].replace('_', ' ')) for x in sqlutils.get_filtered_ideas(config['dbinfo'])]


def get_ideas_by_category(ideas, interests, skills, site, categories):
    """ ideas = {topic1: [{profile: x, profile_id: y}, ...],
                 skill1: [...],
                 skill2: [...],
                ...
                }
    """
    interest_dict = {k: v for k, v in zip(categories['people']['topics'], categories['ideas']['topics'])}
    skill_dict = {k: v for k, v in zip(categories['people']['skills'], categories['ideas']['skills'])}

    idea_interests = [interest_dict.get(interest) for interest in interests]
    idea_skills = [skill_dict.get(skill) for skill in skills]

    # Lazy loading of ideas by skill and interest
    for interest in idea_interests:
        if interest not in ideas:
            ideas[interest] = mbapi.get_all_category_members(interest, site)
        else:
            pass

    for skill in idea_skills:
        if skill not in ideas:
            ideas[skill] = mbapi.get_all_category_members(skill, site)
        else:
            pass

    if idea_interests is [] and idea_skills is [] and 'all' not in ideas:
        ideas['all'] = mbapi.get_all_category_members(categories['ideas']['all ideas'], site)
    else:
        pass

###### put in hideously complicated combinatoric stuff ^_^
    # What to return
    ideas_list = []
    if interests and skills:
        for idea_interest in idea_interests:
            for idea_skill in idea_skills:
                filtered_ideas = [x for x in ideas[idea_skill] if x in ideas[idea_interest] and x not in ideas_list]
                print('{}/{}: {}'.format(idea_skill, idea_interest, filtered_ideas))
                ideas_list.extend(filtered_ideas)
    elif interests:
        for idea_interest in idea_interests:
            filtered_ideas = [x for x in ideas[idea_interest] if x not in ideas_list]
            ideas_list.extend(filtered_ideas)
    elif skills:
        for idea_skill in idea_skills:
            filtered_ideas = [x for x in ideas[idea_skill] if x not in ideas_list]
            ideas_list.extend(filtered_ideas)
    else:
        ideas_list = ideas['all']
    print ideas_list
    return ideas_list


def filter_ideas(ideas, active_ideas):
    return [x for x in ideas if x['profile_title'] in active_ideas]


def choose_ideas(ideas, number_to_choose):
    try:
        return random.sample(ideas, number_to_choose)
    # this is raised if number_to_choose is larger than the list, or negative
    except ValueError:
        return ideas


def get_more_ideas():
    pass


def postinvite(pagetitle, greeting, topic, site):
    """Add a new section to a page, return the API POST result."""
    profile = site.Pages[pagetitle]
    result = profile.save(greeting, section='new', summary=topic)
    return result


def collect_match_info(response, profile_dict, matched_ideas, run_time):
    """
    participant_userid INTEGER,
    p_profile_pageid INTEGER,
    p_interest VARCHAR(75),
    p_skill VARCHAR(75),
    request_time DATETIME,
    match_time DATETIME,
    match_revid INTEGER,
    idea_pageid INTEGER,
    run_time DATETIME,"""

    match_info = []
    for idea in matched_ideas:
        match_info.append({
            'participant_userid': profile_dict['userid'],
            'p_profile_pageid': profile_dict['profile_id'],
            'p_interest': None,
            'p_skill': None,
            'request_time': utils.parse_timestamp(profile_dict['cat_time']),
            'match_time': utils.parse_timestamp(response['newtimestamp']),
            'match_revid': response['newrevid'],
            'idea_pageid': idea['profileid'],
            'run_time': run_time
        })
    return match_info


def main(filepath):
    run_time = datetime.datetime.utcnow()
    config = utils.load_config(filepath)
    edited_pages = False
    wrote_db = False
    logged_errors = False
    try:
        prevruntimestamp = utils.timelog(run_time, filepath)
    except Exception as e:
        mblog.logerror(u'Could not get time of previous run', exc_info=True)
        logged_errors = True
        sys.exit()

    site = login(config['login'])

    profile_lists = get_profiles(prevruntimestamp, config['categories'], site)
    bare_profiles = filter_profiles(profile_lists[0], profile_lists[1], config['pages']['main'])
    new_profiles = get_profile_info(bare_profiles, config['categories'], config['pages'], site)
    print(new_profiles)

    active_ideas = get_active_ideas(run_time, config)
    ideas = {}

    for profile in new_profiles:
        skills = new_profiles[profile]['skills']
        interests = new_profiles[profile]['interests']

        idea_list = get_ideas_by_category(ideas, interests, skills, site, config['categories'])
        active_idea_list = filter_ideas(idea_list, active_ideas)
        final_ideas = choose_ideas(active_idea_list, 3)

        if len(final_ideas) < 3:
            get_more_ideas()
        # TODO: what if there aren't enough ideas? NOTE will probably have to rework this also for multiple interests/skills

        greeting = utils.buildgreeting(config['greetings']['greeting'], new_profiles[profile]['username'], final_ideas)

        try:
            response = postinvite(new_profiles[profile]['talk_title'], greeting, 'Ideas for you', site)
            edited_pages = True
        except mwclient.MwClientError as e:
            mblog.logerror(u'Could not post match on {}\'s page'.format(
                profile['username']), exc_info=True)
            logged_errors = True
            continue

        match_info = collect_match_info(response, new_profiles[profile], final_ideas, run_time)
        sqlutils.logmatch(match_info, config['dbinfo'])
        wrote_db = True

        try:
            pass
        except Exception as e:
            mblog.logerror(u'Could not write to DB for {}'.format(
                learner['learner']), exc_info=True)
            logged_errors = True
            continue
    print ideas
    mblog.logrun(filepath, run_time, edited_pages, wrote_db, logged_errors)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = './matching/'

    main(filepath)
