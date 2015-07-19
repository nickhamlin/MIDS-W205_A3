# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 17:05:38 2015

@author: nicholashamlin
http://www.laurentluce.com/posts/upload-and-download-files-tofrom-amazon-s3-using-pythondjango/
"""
import json
import os

import pymongo
from boto.s3.connection import S3Connection
from boto.s3.key import Key

awsconn = S3Connection('AKIAI5Z33FRUEKBGOWFA', 'y2JLQ8x6sSOvHP3CmmDe49X/NEQrN88PGTRP5CVL')
myBucket = awsconn.get_bucket('hamlin-mids-assignment3')
myKey = Key(myBucket)

#connect to Mongo
try:
    conn=pymongo.MongoClient()
    print "Connected!"
except pymongo.errors.ConnectionFailure, e:
   print "Connection failed : %s" % e 

db_tweets = conn['db_tweets']
tweets = db_tweets.tweets
tweets.remove()

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
                #put some logging here
                fail+=1
        print str(success)+' tweets entered, '+str(fail)+' failed from '+str(fname)
            
if __name__=='__main__':
    for chunk in myBucket.list():
        keyString = str(chunk.key)
        if keyString[0]=='#':
            #download from s3 if you haven't already
            if not os.path.exists(keyString):
                chunk.get_contents_to_filename(keyString)
            load_tweets(keyString)
            print str(tweets.count())+' are currently stored'
           