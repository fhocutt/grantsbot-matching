#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
mbapi
~~~~~

This module contains customized API calls and associated helper methods
for MatchBot.
"""

import json
import time

import utils


def get_page_title(pageid, site):
    """ Get page title from page id. """
    response = site.api(action='query',
                        prop='info',
                        pageids=pageid)
    title = parse_page_title_response(response)
    return title


def parse_page_title_response(response):
    pagedict = response['query']['pages']
    for page in pagedict:
        title = pagedict[page]['title']
    return title


def get_page_info(title, categories, site):
    """ OUTDATED
     Retrieve user information for the user who made the first edit
    to a page.
    Parameters:
        title   :   a string containing the page title
        site    :   a mwclient Site object associated with the page

    Returns:
        user    :   a string containing the page creator's user name
        userid  :   a string containing the page creator's userid

        categories = list of dicts of the form {"ns": 14, "title": "Category:Blah"}
    """
    category_string = utils.make_category_string(categories)
    response = site.api(action='query',
                        prop='revisions|info|categories',
                        rvprop='user|userid',
                        rvdir='newer',
                        inprop='talkid',
                        cllimit='max',
                        clcategories=category_string,
                        titles=title,
                        rvlimit=1)
    page_info = parse_page_info_response(response)
    return page_info


def parse_page_info_response(response):
    pagedict = response['query']['pages']
    for page in pagedict:
        user = pagedict[page]['revisions'][0]['user']
        userid = pagedict[page]['revisions'][0]['userid']
        talkid = pagedict[page].get('talkid')
        page_categories = pagedict[page].get('categories')
    return (user, userid, talkid, page_categories)


def get_new_members(categoryname, site, timelastchecked):
    """Get information on all pages in a given category that have been
    added since a given time.

    Parameters:
        category        :   a string containing the category name,
                            including the 'Category:' prefix
        site            :   mwclient Site object corresponding to the
                            desired category
        timelastchecked :   a MediaWiki-formatted timestamp

    Returns:
        a list of dicts containing information on the category members.

    Handles query continuations automatically.
    """
    recentkwargs = {'action': 'query',
                    'list': 'categorymembers',
                    'cmtitle': categoryname,
                    'cmprop': 'ids|title|timestamp',
                    'cmlimit': 'max',
                    'cmsort': 'timestamp',
                    'cmdir': 'older',
                    'cmend': timelastchecked}
    result = site.api(**recentkwargs)
    newcatmembers = add_members_to_list(result, categoryname)

    while True:
        if 'continue' in result:
            newkwargs = recentkwargs.copy()
            for arg in result['continue']:
                newkwargs[arg] = result['continue'][arg]
            result = site.api(**newkwargs)
            newcatmembers = add_members_to_list(result, categoryname,
                                            newcatmembers)
        else:
            break
    return newcatmembers


def add_members_to_list(result, categoryname, catusers=None):
    """Create a list of dicts containing information on each user from
    the getnewmembers API result.

    Parameters:
        result      :   a dict containing the results of the
                        getnewmembers API query
        catusers    :   a list of dicts with information on category
                        members from earlier queries. Optional,
                        defaults to None.

    Returns:
        a list of dicts containing information on the category members
        in the provided query.
    """
    if catusers is None:
        catusers = []
    else:
        pass

    for page in result['query']['categorymembers']:
        userdict = {'profile_id': page['pageid'],
                    'profile_title': page['title'],
                    'cat_time': page['timestamp'],
                    'category': categoryname}
        catusers.append(userdict)
    return catusers


def get_all_category_members(category, site):
    """Get information on all members of a given category

    Parameters:
        category:   a string containing the category name, including
                    the 'Category:' prefix
        site    :   mwclient Site object corresponding to the desired
                    category

    Returns:
        a list of dicts containing information on the category members.

    Handles query continuations automatically.
    """
    kwargs = {'action': 'query',
              'list': 'categorymembers',
              'cmtitle': category,
              'cmprop': 'ids|title',
              'cmlimit': 'max'}
    result = site.api(**kwargs)
    catmembers = addmentorinfo(result)
    while True:
        if 'continue' in result:
            newkwargs = kwargs.copy()
            for arg in result['continue']:
                newkwargs[arg] = result['continue'][arg]
            result = site.api(**newkwargs)
            newcatmembers = addmentorinfo(result, catmembers)
        else:
            break
    return catmembers


def addmentorinfo(result, catmembers=None):
    """Create a list of dicts containing information on each user from
    the getallcatmembers API result.

    Parameters:
        result      :   a dict containing the results of the
                        getallmembers API query
        catusers    :   a list of dicts with information on category
                        members from earlier queries. Optional,
                        defaults to [].
    Returns:
        a list of dicts containing information on the category members
        in the provided query.
    """
    if catmembers is None:
        catmembers = []
    else:
        pass

    for page in result['query']['categorymembers']:
        userdict = {'profileid': page['pageid'], 'profile_title': page['title']}
        catmembers.append(userdict)
    return catmembers
