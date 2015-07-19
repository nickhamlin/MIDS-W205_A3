 # -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 00:50:19 2015

@author: nicholashamlin

Based on code from: 
http://streamhacker.com/2010/05/10/text-classification-sentiment-analysis-naive-bayes-classifier/
http://stackoverflow.com/questions/3086973/how-do-i-convert-this-list-of-dictionaries-to-a-csv-file-python
"""
import csv

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews

from connections import connect_to_mongo
 
#extract data from NTLK movie reviews corpus and split into train/test sets
def word_feats(words):
    """Processes set of words into NLTK-friendly format"""
    return dict([(word, True) for word in words])

negids = movie_reviews.fileids('neg')
posids = movie_reviews.fileids('pos')
negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]
#define training data as 75% of corpus, reserver the other 25% for model validation
negcutoff = len(negfeats)*3/4
poscutoff = len(posfeats)*3/4
trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]

#train classifier and validate model accuracy using test data
print 'train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats)) 
classifier = NaiveBayesClassifier.train(trainfeats)
print 'accuracy:', nltk.classify.util.accuracy(classifier, testfeats)

if __name__=='__main__':
    #connect to mongo
    conn=connect_to_mongo()  
    db_tweets = conn['db_tweets']
    retweets=db_tweets.retweets
    
    #process tweets and store results in the same collection
    for tweet in list(retweets.find()):
        sentiment=classifier.classify(word_feats(tweet['text']))
        retweets.update({'_id':tweet['_id']}, {"$set": {"sentiment":sentiment}}, upsert=False)
    
    #gather results and save to csv for easy sharing
    to_print=list(retweets.find({},{"_id":1,"screen_name":1,"sentiment":1,"text":1}))
    for i in to_print:
        i['text']=i['text'].replace('\n', ' ').replace('\r', '') #remove newlines
        try:
            i['text'].decode('ascii')
        #Tweets with unicode look bad in CSV, so exlude them (with a note) in the output
        except UnicodeEncodeError:
            i['text']="NOTE: Tweet contains Unicode - can't show in CSV"
    header=['_id','screen_name','sentiment','text'] #define column order for output csv
    with open('sentiment_results.csv', 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, header)
        dict_writer.writeheader()
        dict_writer.writerows(to_print)
    