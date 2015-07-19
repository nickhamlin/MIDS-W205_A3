# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 22:31:30 2015

@author: nicholashamlin
"""
from __future__ import division

from nltk.tokenize import word_tokenize

from connections import connect_to_mongo,connect_to_twitter

#connect to twitter and mongo and create objects for collections we care about
conn=connect_to_mongo()
db_tweets = conn['db_tweets']
tweets = db_tweets.tweets
users = db_tweets.users
api=connect_to_twitter()

def calculate_ld (tweet_list):
    """finds lexical diversity of list of tweets"""
    unified_tweets="".join(tweet_list)
    words=word_tokenize(str(unified_tweets))
    return round(len(set(words))/len(words),4)

#only calculate lexical diversity for a user if we don't have their data already
#since rate limits may force this to run for a long time, we need to be able 
#to pick up where we left off in case of an error.
user_names=list(tweets.distinct("user.screen_name"))
already_recorded=list(users.distinct("user_name"))
to_record=list(set(user_names)-set(already_recorded))

for user in to_record:
    try:
        #collect 50 tweets per user, though this number can be easily changed
        user_tweets = api.user_timeline(screen_name = user,count=50)
    #record situations where a tweet corpus is protected or otherwise unavailable
    except BaseException as e: 
        print 'Error: '+ str(e)
        user_tweets=[]
    tweet_count=len(user_tweets)
    tweets_to_process=[]
    
    #remove non-alphanumeric tweets
    for tweet in user_tweets:
        try:
            tweet.text.decode('ascii')
            tweets_to_process.append(tweet.text)
        except UnicodeEncodeError:
            pass
    
    #calculate lexical diversity
    if len(tweets_to_process)>0:
        ld=calculate_ld(tweets_to_process)
        status='ok'
    #record situations where no alphanumeric tweets are available for a user
    else:
        tweet_count=0
        ld=0
        status='N/A: No tweets available'
    
    #write result to mongo
    users.insert({'user_name':user,
                   'tweet_count':tweet_count,
                   'lexical_diversity':ld,
                   'status':status})
    
    #this isn't necessary, but is useful for keeping an eye on the program as it runs
    print str(user)+' complete with lexical diversity='+str(ld)+' across '+str(tweet_count)+' tweets '