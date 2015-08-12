#!/bin/sh

echo 'starting mongodump...'
/Users/nicholashamlin/mongodb/bin/mongodump --collection tweets --db db_tweets
echo 'mongodump complete, uploading to s3...'
aws s3 sync ./dump s3://hamlin-mids-assignment3/mongobackup
echo 'cleaning up...'
rm -rf ./dump
echo 'done!'
