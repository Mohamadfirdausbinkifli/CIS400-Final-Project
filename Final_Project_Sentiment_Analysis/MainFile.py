#CIS400 Final Project
#@author Sam Ansell
import twitter
import json
import requests
import datetime
import time
from helperFunctions import *
from pymongo import MongoClient
from flask import Flask

appFlask = Flask(__name__)

@appFlask.route('/api/todays_sentiment/')
def main():
    #getting twitter keys and tokens authenticated
    twitter_api = oauth_login()
    #screen_name = 'sansellviolin'
    #current_user_id = 940631
    q = "PUBG" #query for twitter_search function
    max_results = 10000 #maximum number of tweets retreived by the twitter_search function
    results = twitter_search(twitter_api, q, max_results)

    db = getConnect()

    '''-create dictionary with keys: text, query, topic, gaming, id
       -populate dictionary with tweets from results function'''
    requestBody = {}
    requestBody = {'data': []}
    for i in range (0, len(results)):
        requestBody['data'].append({'text': results[i]['text'],  'id': i,
                                    'query': 'PUBG', 'topic': 'gaming'})

    '''use HTTP POST request to access Sentiment140 api'''
    r = requests.post("http://www.sentiment140.com/api/bulkClassifyJson?appid=sansell@syr.edu", json.dumps(requestBody))
    print r
    #setting the json formatted response of the HTTP POST request to the variable responseBody
    responseBody = r.json()
    #putting the polarity key values into a list, then sorting it in accending order
    sentimentScores = sorted([li['polarity'] for li in responseBody['data']], reverse=False)
    print sentimentScores

    #creating the net sentiment score for the set of tweets
    neutralCounter = 0
    positiveCounter = 0
    negativeCounter = 0
    netSentimentScore = 0
    x = 0
    while x in range (len(sentimentScores)):
        if(sentimentScores[x] == 0):
            negativeCounter+=1
        elif(sentimentScores[x] == 2):
            neutralCounter+=1
        elif(sentimentScores[x] == 4):
            positiveCounter+=1
        x+=1
    posAndNeg = positiveCounter + negativeCounter
    netSentimentScore = float(positiveCounter) / float(posAndNeg)
    nSSstring = str(netSentimentScore)
    print "neutral: " + str(neutralCounter)
    print "negative: " + str(negativeCounter)
    print "positive: " + str(positiveCounter)
    print "net-Sentiment Score Ratio: " + nSSstring[:3]

    #creating a dictionary of the current date and its reapective sentiment score
    dictNetSentimentScore = {'daily_sentiment_score': nSSstring[:3], 'date': currentDate()}

    '''using the MongoDB and mLab APIs'''
    #setting the route for the sentiment scores in the database
    sentiment_scores_collection = db['sentiment_scores_collection']
    #posting the dictNetSentimentScore to the collection in mLab
    sentiment_scores_collection.insert_one(dictNetSentimentScore)
    test = dictNetSentimentScore['daily_sentiment_score']
    print test
    return test


@appFlask.route('/api/weeks_sentiment/')
def getWeekSentimentScore():
    total_sentiment_scores_dict = {}
    #retreiving the overarching database from mLab
    db = getConnect()
    #retreiving the collection from the database
    sentiment_scores_collection2 = db['sentiment_scores_collection']
    #querying the database for the last 7 entries from the collection (i.e. the last 7 days)
    total_sentiment_scores_dict = sentiment_scores_collection2.find()
    #setting up a dictionary to be routed to flask
    results = {}
    # Reference used for converting datetime objects to human readable strings:
    # https://stackoverflow.com/questions/10624937/convert-datetime-object-to-a-string-of-date-only-in-python
    #populating that dictionary
    for doc in total_sentiment_scores_dict:
        results[doc['date'].strftime('%m/%d/%Y')] = doc['daily_sentiment_score']

    return json.dumps(results, indent=1)

if __name__ == '__main__':
    main()
    getWeekSentimentScore()
    appFlask.run()
