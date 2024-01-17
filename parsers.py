#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
parses the source html for each group where a parser exists & contributed to the post dictionary
always remember..... https://stackoverflow.com/questions/1732348/regex-match-open-tags-except-xhtml-self-contained-tags/1732454#1732454
'''
import os
import json
import itertools
import asyncio
import time
import requests
from sys import platform
from datetime import datetime

from sharedutils import openjson
from sharedutils import runshellcmd
from sharedutils import todiscord, totwitter, toteams, totelegram, tovenari
from sharedutils import stdlog, dbglog, errlog, honk

# on macOS we use 'grep -oE' over 'grep -oP'
if platform == 'darwin':
    fancygrep = 'grep -oE'
else:
    fancygrep = 'grep -oP'

def posttemplate(victim, group_name, timestamp):
    '''
    assuming we have a new post - form the template we will use for the new entry in posts.json
    '''
    schema = {
        'post_title': victim,
        'group_name': group_name,
        'discovered': timestamp
    }
    dbglog(schema)
    return schema

def existingpost(post_title, group_name):
    '''
    check if a post already exists in posts.json
    '''
    posts = openjson('posts.json')
    # posts = openjson('posts.json')
    for post in posts:
        if post['post_title'] == post_title and post['group_name'] == group_name:
            #dbglog('post already exists: ' + post_title)
            return True
    dbglog('post does not exist: ' + post_title)
    return False

def appender(post_title, group_name):
    '''
    append a new post to posts.json
    '''
    if len(post_title) == 0:
        errlog('post_title is empty')
        return
    # limit length of post_title to 90 chars
    if len(post_title) > 180:
        post_title = post_title[:180]
    if existingpost(post_title, group_name) is False:
        posts = openjson('posts.json')
        newpost = posttemplate(post_title, group_name, str(datetime.today()))
        stdlog('adding new post - ' + 'group:' + group_name + ' title:' + post_title )
        posts.append(newpost)
        with open('posts.json', 'w', encoding='utf-8') as outfile:
            '''
            use ensure_ascii to mandate utf-8 in the case the post contains cyrillic 🇷🇺
            https://pynative.com/python-json-encode-unicode-and-non-ascii-characters-as-is/
            '''
            dbglog('writing changes to posts.json')
            json.dump(posts, outfile, indent=4, ensure_ascii=False)
        # if socials are set try post
        if os.environ.get('DISCORD_WEBHOOK') is not None:
            todiscord(newpost['post_title'], newpost['group_name'])
        if os.environ.get('TWITTER_ACCESS_TOKEN') is not None:
            totwitter(newpost['post_title'], newpost['group_name'])
     #   if os.environ.get('MS_TEAMS_WEBHOOK') is not None:
     #       toteams(newpost['post_title'], newpost['group_name'], newpost['url'], newpost['date_posted'], newpost['leak_size'], newpost['leak_status'])
        if os.environ.get('TELEGRAM_TOKEN') is not None:
            asyncio.run(totelegram(newpost['post_title'], newpost['group_name']))
        if os.environ.get('API_KEY') is not None:
            tovenari(newpost['post_title'], newpost['group_name'], newpost['discovered'])
'''
all parsers here are shell - mix of grep/sed/awk & perl - runshellcmd is a wrapper for subprocess.run
'''

def no_name():
    stdlog('parser: ' + 'cloak')
    parser_name = '''
    cat source/no-name-*.html | sed 's/>/\\n/g' | grep -A 2 'class="uagb-post__title uagb-post__text"' | grep -v 'class="uagb-post__title uagb-post__text"' | grep -v '<a href=' | grep -v '^-' | cut -f 1 -d '<'
    '''
    #parser_description = '''
    #jq -r '.data[].text' source/royal-*.html
    #'''
    #parser_url = '''
    #jq -r '.data[].url' source/royal-*.html
    #'''
    #parser_post_link = '''
    #'''
    #parser_country = '''
    #cat source/cloak-*.html | grep '<p class="main__country">' | cut -f 2 -d ':' | sed 's/^ //g' | cut -f 1 -d '<'
    #'''
    #parser_date = '''
    #jq -r '.data[].time' source/royal-*.html
    #'''
    #parser_size = '''
    #jq -r '.data[].size' source/royal-*.html
    #'''
    #parser_status = '''
    #jq -r '.data[].percentage' source/royal-*.html
    #'''
    names = runshellcmd(parser_name)
    #descriptions = runshellcmd(parser_description)
    #urls = runshellcmd(parser_url)
    #post_links = runshellcmd(parser_post_link)
    #countries = runshellcmd(parser_country)
    #dates = runshellcmd(parser_date)
    #sizes = runshellcmd(parser_size)
    #statuses = runshellcmd(parser_status)
    if len(names) == 1:
        errlog('no-name: ' + 'parsing fail')
    for name in names:
        appender(name, 'no-name')
