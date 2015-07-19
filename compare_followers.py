# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 23:00:45 2015

@author: nicholashamlin
"""
import csv

from connections import connect_to_mongo

#connect to mongo and create objects for collections we want to use   
conn=connect_to_mongo()
db_tweets = conn['db_tweets']
db_followers = conn['db_followers']
retweets=db_tweets.retweets
followers = db_followers.followers

def find_unfollowers(screen_name,start_date,end_date):
    """given two dates, return a list of follower ids 
    who existed at the first date, but not the second, for a given user"""
    
    prev_users=list(followers.find({"following":screen_name,"following_as_of":start_date},{'_id':0,'id':1}))
    prev_users=[i['id'] for i in prev_users]
    current_users=list(followers.find({"following":screen_name,"following_as_of":end_date},{'_id':0,'id':1}))
    current_users=[i['id'] for i in current_users]
    unfollowers=list(set(prev_users)-set(current_users))
    return unfollowers


if __name__=="__main__":
    #find the top 10 users within the top 30 most retweeted tweets
    pipeline = [
    {"$group": {"_id": "$screen_name"}},
    {"$sort": {"followers_count":-1}}]
    most_followed=list(retweets.aggregate(pipeline))[:10]

    #print results for each user showing how different their first 10K followers
    #are from one date to another
    to_print=[]
    for user in most_followed:
        name=user['_id']
        lost=find_unfollowers(name,'2015-07-11','2015-07-17')
        print str(len(lost))+' '+user['_id']
        to_print.append({"user":user['_id'],"followers_lost":len(lost)})
    
    #write results to csv
    header=['user','followers_lost'] #define column order for output csv
    with open('lost_followers_by_user.csv', 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, header)
        dict_writer.writeheader()
        dict_writer.writerows(to_print)