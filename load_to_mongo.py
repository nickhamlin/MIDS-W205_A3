# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 17:05:38 2015

@author: nicholashamlin
"""
import json
import os

import pymongo
from connections import connect_to_s3,connect_to_mongo
from boto.s3.key import Key

#connect to AWS
awsconn =connect_to_s3()
myBucket = awsconn.get_bucket('hamlin-mids-assignment3')
myKey = Key(myBucket)

#connect to Mongo
conn=connect_to_mongo()
db_tweets = conn['db_tweets']
tweets = db_tweets.tweets
#Use following line to purge any existing tweets in the mongo collection - used for debugging
#tweets.remove()

def load_tweets(fname):
    """ Loads tweets from locally stored json to mongodb"""
    with open(fname,'rb') as to_read:
        tweets_to_load=json.load(to_read)
        success=0
        fail=0
        for tweet in tweets_to_load:
            try:
                tweets.insert(tweet)
                success+=1
            except:
                fail+=1
        #not required - but useful for debugging
        print str(success)+' tweets entered, '+str(fail)+' failed from '+str(fname)

if __name__=='__main__':
    for chunk in myBucket.list():
        keyString = str(chunk.key)
        if keyString[0]=='#': #only pay attention to files starting with a hashtag
            #download from s3 if file doesn't exist locally already
            if not os.path.exists(keyString):
                chunk.get_contents_to_filename(keyString)
            load_tweets(keyString)
            #not required - but useful for debugging
            print str(tweets.count())+' are currently stored'
