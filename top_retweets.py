# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 23:52:32 2015

@author: nicholashamlin
"""
from connections import connect_to_mongo

#connect to mongo
conn=connect_to_mongo()
db_tweets = conn['db_tweets']
tweets = db_tweets.tweets
retweets=db_tweets.retweets

#get top 30 most retweeted tweets
pipeline = [
    {"$group": {"_id": "$retweeted_status.id", "count":{"$max":"$retweeted_status.retweet_count"}}},
    {"$sort": {"count":-1}}]

top_retweets=list(tweets.aggregate(pipeline))[:30]

#insert tweet and metadata into db_tweets.retweets
for tweet in top_retweets:
    to_insert=list(tweets.find({"retweeted_status.id":tweet["_id"]}))[0]
    json={"retweet_id":tweet["_id"],
          "screen_name":to_insert['retweeted_status']['user']['screen_name'],
          "location":to_insert['retweeted_status']['user']['location'],
          "text":to_insert['retweeted_status']['text'],
          "retweets":tweet["count"],
          "followers_count":to_insert['retweeted_status']['user']['followers_count']
          }
    retweets.insert(json)

