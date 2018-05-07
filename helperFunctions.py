#CIS400 Final Project
#@author Sam Ansell
import twitter
import sys
import datetime
import time
from pymongo import MongoClient
from flask import Flask

def oauth_login():
    # XXX: Go to http://twitter.com/apps/new to create an app and get values
    # for these credentials that you'll need to provide in place of these
    # empty string values that are defined as placeholders.
    # See https://dev.twitter.com/docs/auth/oauth for more information
    # on Twitter's OAuth implementation.

    CONSUMER_KEY = 'SERYTAxk0dSmdETcRNQdH29g7'
    CONSUMER_SECRET = 'w39G7kACRu57Y9WTCU0WPTAfWzJTo8i8L3I2ys6VEXdWoIT0GJ'
    OAUTH_TOKEN = '954068493070159873-EFXZmSKAUUIwy1rEl8DS8ZbtGM0pcqc'
    OAUTH_TOKEN_SECRET = 'p07V3vVo7CJfgkR9bmpXxhLTdlfIvgmC9nkbBUBu3KrMe'
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    #authenticating the twitter keys and tokens
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api


def twitter_search(twitter_api, q, max_results, **kw):
    search_results = twitter_api.search.tweets(q=q, count=max_results, **kw)
    statuses = search_results['statuses']

    # Enforce a reasonable limit
    max_results = min(1000, max_results)
    for _ in range(1000): # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError, e: # No more results when next_results doesn't exist
            break

        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([ kv.split('=') for kv in next_results[1:].split("&") ])
        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']
        if len(statuses) > max_results:
            break

    return statuses




def currentDate():
    #getting the current date
    currentDate = datetime.datetime.now()
    return currentDate


def getConnect():
    '''MongoDB and mLab stuff'''
    #connecting to the MongoDB & mLab clients
    mongoClient = MongoClient('mongodb://SamAnsellMLab:Password123@ds215380.mlab.com:15380/sentiment_scores')
    #accessing the overarching database
    db = mongoClient.sentiment_scores

    return db
