from joetools import private
import datafreeze
from datafreeze import freeze
import tweepy
import dataset
from textblob import TextBlob

db = dataset.connect(private.CONNECTION_STRING)

result = db[private.TABLE_NAME].all()
freeze(result, format='csv', filename=private.CSV_NAME)