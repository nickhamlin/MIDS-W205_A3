# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 21:59:32 2015

@author: nicholashamlin
"""
import json
import threading
import datetime
import time

import tweepy
from boto.s3.key import Key

from connections import connect_to_twitter,connect_to_s3

conn=connect_to_s3()
myBucket = conn.get_bucket('hamlin-mids-assignment3')
myKey = Key(myBucket)


class TweetSerializer:
   out = None
   first = True
   count = 0
   tweet_count=0
   
   def write_to_s3 (self,file):
        """ Given a file, upload it to S3 bucket specified below"""
        myKey.key = file.name
        try:
            myKey.set_contents_from_filename(file.name)
        except Exception as e:
            print 'Error, Upload to S3 failed: '+ str(e)
        return
        
   def start(self,term,start_time):
      self.count += 1
      self.tweet_count=0
      fname = str(term)+"-"+str(start_time)+"-"+str(self.count)+".json"
      self.out = open(fname,"w")
      self.out.write("[\n")
      self.first = True

   def end(self):
      if self.out is not None:
         self.out.write("\n]\n")
         self.out.close()
         self.write_to_s3(self.out)
         print str(self.out.name)+' completed and uploaded to S3'
      self.out = None

   def write(self,tweet):
      if not self.first:
         self.out.write(",\n")
      self.first = False
      self.out.write(json.dumps(tweet._json).encode('utf8'))
      self.tweet_count+=1
      

api=connect_to_twitter()
        
def gather_tweets (start,end,query,threshold):
    print "Starting search for "+query
    query_start=start
    lock=threading.RLock()
    query_end=query_start+datetime.timedelta(days = 1)
    serializer = TweetSerializer()
    serializer.start(query, query_start)        
    while query_start <= end:
        try:
            for tweet in tweepy.Cursor(api.search,q=query, since = query_start, until = query_end).items():
                with lock:
                    serializer.write(tweet)
                    if serializer.tweet_count==threshold:
                        serializer.end()
                        serializer.start(query, query_start)
            serializer.end()
            query_start = query_start + datetime.timedelta(days = 1)
        except KeyboardInterrupt:
            print 'Manually stopping...'
            serializer.end()
            break
        except BaseException as e:
            print 'Error, program failed: '+ str(e)
            time.sleep(60)

if __name__=="__main__":
    end=datetime.date.today()
    start=datetime.date(2015,7,6)
    search1='#USAvJPN'
    search2='#WorldCupFinal'
    gather_tweets(start,end,search1,10000)
    gather_tweets(start,end,search2,10000)