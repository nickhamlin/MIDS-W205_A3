#!/bin/sh

mkdir ./dump
echo 'downloading from s3...'
aws s3 sync s3://hamlin-mids-assignment3/mongobackup ./dump
echo 'restoring mongo databases...'
mongorestore ./dump
echo 'cleaning up...'
rm -rf ./dump
echo 'done!'
