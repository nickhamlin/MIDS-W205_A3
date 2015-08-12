# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 17:42:39 2015

@author: nicholashamlin
Based on explanations at https://bespokeblog.wordpress.com/2011/07/11/basic-data-plotting-with-matplotlib-part-3-histograms/
"""
import matplotlib.pyplot as plt
import numpy as np

from connections import connect_to_mongo

#connect to mongo
conn=connect_to_mongo()
db_tweets = conn['db_tweets']
users = db_tweets.users
retweets=db_tweets.retweets

#load all lexical diversity scores into a list, excluding N/A statuses
to_plot=[i['lexical_diversity'] for i in list(users.find({"status": {"$ne":"N/A: No tweets available"}},{'_id':0,'lexical_diversity':1}))]

#create plot
plt.hist(to_plot, bins=50,color='b')
plt.title("Lexical Diversity for Users in db_tweets.users")
plt.xlabel("Value")
plt.ylabel("Frequency")

#add vertical lines for top users
top_users=list(retweets.distinct("screen_name"))
for i in top_users:
    try:
        ld=list(users.find({"user_name":i},{"_id":0,"lexical_diversity":1}))[0]
        plt.axvline(ld['lexical_diversity'],linewidth=2,color='g')
    #skip users if we're missing lexical diversity data for them
    except IndexError:
        continue

#add vertical line for means
mean=np.mean(to_plot)
print "Mean lexical diversity is "+str(mean) #for reference
plt.axvline(mean,linewidth=2,color='r')

#save result to PNG file
plt.savefig('lexical_diversity_histogram.png', bbox_inches='tight')
