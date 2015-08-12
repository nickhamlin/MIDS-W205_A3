# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 19:19:02 2015

@author: nicholashamlin
"""
import time
import datetime

import tweepy

from connections import connect_to_mongo, connect_to_twitter

#set up connections to twitter and mongo
api=connect_to_twitter()
conn=connect_to_mongo()
db_tweets = conn['db_tweets']
db_followers = conn['db_followers']
retweets=db_tweets.retweets
followers=db_followers.followers

def gather_followers (screen_name):
    """stores first 10K follower ids for a given twitter screen name"""
    print "Starting search for "+screen_name #not required, but nice for monitoring progress
    today=str(datetime.date.today())

    #This WHILE structure allows for easy error handling if the connection encounters problems
    while True:
        try:
            #Change the number in the following line to capture more/less followers
            for user in tweepy.Cursor(api.followers_ids, screen_name=screen_name).items(10000):
                followers.insert_one({'id':user,'following':screen_name,'following_as_of':today})
            break
        except KeyboardInterrupt:
            print 'Manually stopping...'
            break
        except BaseException as e:
            print 'Error, program failed: '+ str(e)
            time.sleep(60)

if __name__=="__main__":
    for user in list(retweets.distinct("screen_name")):
        gather_followers(user)
