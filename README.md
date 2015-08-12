#Nick Hamlin - Assignment 3

##1. Summary of Outputs:
###1.1 Code Files
- **connections.py**: Defines functions for connecting to twitter, mongo, and S3 in one file, which means that credentials need only be stored in one place.
- **store_tweets.py**: Gathers tweets for specified hashtags from the Twitter Search API, serializes into json files chunked by date with an optional maximum number of tweets per file (I've chosen 10,000).  These results are immediately uploaded to S3 as soon as they are completed to ensure they're fully backed up.
- **load_to_mongo.py**: Extracts chunked tweets and automatically loads them (one tweet per document) into a MongoDB collection.  For speed, if a file that is stored in S3 also happens to exist locally already, this file will not download a redundant copy again.
- **top_retweets.py**: Queries the Mongo tweet collection to identify the top 30 most retweeted tweets.  These tweets, along with user and location metadata, are then written to a separate collection called "retweets" in the same mongo database.
- **lexical_diversity.py**: Calculates lexical diversity for the first 50 available tweets from each user represented in db_tweets.tweets and stores the results to db_tweets.users.
- **create_histogram.py**: Uses matplotlib to create a histogram of all lexical diversities gathered and highlights those of key users.
- **get_followers.py**: Gathers the first 10,000 followers for each user appearing in the list of top 30 retweets stored in the "retweets" collection and stores the result in a separate database (db_followers) in a collection called "followers".  Twitter's rate limiting makes it impractical to gather all followers, especially for very famous users with vast fan bases, which is why I'm limiting my data collection to the first 10,000 results.  Luis confirmed that this was an appropriate design choice during office hours on July 9.
- **compare_followers.py**: Identifies the differences in lists of followers between two dates by querying the "followers" collection stored in db_followers.
- **sentiment_analysis.py**: Uses NTLK to implement a basic positive/negative sentiment analysis of the text of the top 30 retweets stored in db_tweets.retweets using a Naive Bayes model.
- **backup.sh**: Creates a backup of db_tweets and automatically uploads it to S3.
- **restore.sh**: Automatically downloads the mongo backups from S3 and rebuilds them locally.


###1.2 Supporting Files
- **links_to_data.txt** All chunked sets of tweets and backups of the mongo databases are stored in [this AWS bucket](https://s3-us-west-2.amazonaws.com/hamlin-mids-assignment3).  For convenience, this file contains a list of direct links to each individual chunk.  In addition, the mongo backups are stored the the same s3 bucket in the "mongobackup" folder.
- **lexical_diversity_histogram.png**: Shows a histogram of all lexical diversities scored collected, along with scores of popular users for comparison.
- **sentiment_analysis.csv**: The sentiment analysis results for the top 30 retweets are included in this CSV file
- **lost_followers_by_user.csv**: A list of the top 10 users appearing in db_tweets.retweets, along with the number of followers lost between July 11 and July 17 out of the first available 10,000 followers per user.

###1.3 MongoDB databases and collections
- **db_tweets**: Main database containing the following collections
  - *tweets*: primary tweet corpus
  - *retweets*: top 30 retweets, with associated user data
  - *users*: lexical diversity information for users represented in db_tweets.tweets
- **db_followers**: Secondary database with follower information
  - *followers*: contains id numbers for first 10,000 followers for each user represented in db_tweets.retweets

##2. Program Design
###2.1 Tweet Collection and Storage
Since this assignment required heavy use of the twitter REST api and I had based my solution to Assignment 2 on the Streaming api, I essentially repeated assignment 2 and rewrote my tweet collection apparatus to use the REST api.  Because tweets for the original hashtags were no longer available via the REST api, I chose two new hashtags on which there was significant recent activity: #USAvsJPN and #WorldCupFinal. Between these two hashtags, I collected a total volume of 412,522 tweets.

Because of the practical restrictions imposed by twitter's rate limits, it did not make sense to download the same set of tweets twice, once to chunk and upload to S3 and another directly from twitter into Mongo.  For this reason, I chose to gather these tweets once and save them automatically to S3.  I then automatically downloaded them from S3 and loaded them into Mongo. Since the results would be the same had I downloaded them from S3 and then also downloaded them directly into Mongo, I decided to create one single collection of tweets, db_tweets.tweets, rather than two duplicate versions. Luis confirmed that this was an acceptable design choice during office hours on July 9.

###2.2 Follower Collection, Storage, and Identification of Lost Followers
Since only a unique id is required to identify a follower, I chose to only store the twitter id numbers of each follower in db_followers.followers to minimize the amount of required storage and maximize scalability.  With a high-profile topic like the Women's World Cup final, many highly-followed users were tweeting. As rate limiting would make collecting the millions of followers for these users impossible within the time limits for this assignment, I gathered the first 10,000 followers available for each of the users represented in db_tweets.retweets.  To find those people who stopped following a particular user, I compared the first 10,000 followers as of July 11 with the first 10,000 followers as of July 17 via a simple set of mongo queries.  The results for each user are then printed and saved to a csv ("lost_followers_by_user.csv").

###2.3 Data analysis
####2.3.1 Lexical Diversity
Within the corpus of 400k+ tweets gathered for this assignment, there are over 110K unique users represented. Because of rate limiting restrictions imposed by twitter, analyzing the complete tweet corpuses for each of these users would take weeks to process.  As a result, I'm gathering the first 50 available tweets for each user to calculate their lexical diversity, excluding any tweets that contain non-alphanumeric characters.  For each user, I log the screen name, lexical diversity, and total number of tweets analyzed in a mongo collection (db_tweets.users), as well as a 'status' for each user indicating if the program has run successfully for their tweets. If a user's tweet corpus isn't in English, or if they have restricted the access to their tweets, a status message of 'N/A: No tweets available' is logged in mongo along with a default lexical diversity value of 0.  This allows for quick identification of problems in analyzing the results.

For the output histogram, I plotted lexical diversities for all the users recorded.  In addition, I added vertical lines to indicate the mean of the overall dataset (in red) and the individual lexical diversities of the users represented in db_tweets.retweets (in green).  Interestingly, this plot reveals that the most popularly retweeted users within the dataset have lower than average lexical diversities, which may indicate that popular content on twitter tends to be more simplistic.

####2.3.2 Sentiment Analysis
NLTK contains both support for binary sentiment analysis classifiers, as well as a corpus of movie reviews that are tagged as either positive or negative.  For simplicity, I used this corpus, even though the types of words that one might use in a movie review may be different than the vocabulary of a typical twitter user.  For classification, I used NTLK's implementation of a [Naive Bayes model](https://en.wikipedia.org/wiki/Naive_Bayes_classifier), which treats each tweet as a "bag of words" (order of words is ignored) and assumes that each word contributes independently to the classification of the overall tweet (there is no correlation between words).  Though there are certainly much more sophisticated and precise ways to classify sentiment, Naive Bayes as implemented in NLTK is a simple way to get a classifier running quickly.  In this implementation, it's clear where the Naive Bayes approach breaks down, especially when tweets contain phrases like "the team killed it", which is a positive idea but considered negative based purely on the individual words and the training data alone.  The results of the classifier are both written back to the db_tweets.retweets mongo collection for storage and exported to csv (sentiment_results.csv) for easy viewing.

### 2.4 Backup and restore
I chose to implement backups via a shell script rather than Python because of the simplicity of the implementation.  This approach allows me to use the native mongobackup and mongorestore functionality that is not available via the python pymongo module.  The interaction with S3 is simplified as well by using the Amazon CLI.  As a result, the final implementation is much more streamlined and simpler to debug and scale. The restoration of these backups from s3 takes the same approach.  


##3.Packages used
####Base Python:
- json
- os
- threading
- datetime
- time
- sys
- csv
- division (from __future__ )

####Third Party:
- NLTK (for word tokenization and sentiment analysis)
- matplotlib
- numpy
- Tweepy
- Boto
- Pymongo
- bash (for shell scripts)

##4.Other Useful References:
- http://streamhacker.com/2010/05/10/text-classification-sentiment-analysis-naive-bayes-classifier/
- http://stackoverflow.com/questions/3086973/how-do-i-convert-this-list-of-dictionaries-to-a-csv-file-python
- https://bespokeblog.wordpress.com/2011/07/11/basic-data-plotting-with-matplotlib-part-3-histograms/
- http://www.laurentluce.com/posts/upload-and-download-files-tofrom-amazon-s3-using-pythondjango/
