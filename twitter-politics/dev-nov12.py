from joetools import private
import pandas as pd
import tweepy
import os
import time
import random
import sys
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def environment_variables():
    # Set environment variables
    os.environ['TWITTER_API_KEY'] = private.TWITTER_API_KEY
    os.environ['TWITTER_API_SECRET'] = private.TWITTER_API_SECRET
    os.environ['TWITTER_TOKEN'] = private.TWITTER_TOKEN
    os.environ['TWITTER_TOKEN_SECRET'] = private.TWITTER_TOKEN_SECRET
    
def api_setup():
    '''set up Twitter API'''
    # run to assign environment variables 
    environment_variables()

    # access tweepy authenticator
    auth = tweepy.OAuthHandler(os.environ.get('TWITTER_API_KEY'), os.environ.get('TWITTER_API_SECRET'))
    auth.set_access_token(os.environ.get('TWITTER_TOKEN'), os.environ.get('TWITTER_TOKEN_SECRET'))

    # pass in above authentication to API
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
    return api

def sentiment_analyzer_scores(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    return score

@st.cache
def load_data(tweets_list):
    data = pd.DataFrame(tweets_list)
    return data

def get_user_tweets(api, username):
    # instantiate empty list
    tweets_list = []
    
    for tweet in tweepy.Cursor(api.user_timeline, id=username, tweet_mode='extended').items(100):
        tweet_dict = {'created_at': tweet.created_at,
                     'tweet': tweet.full_text,
                     'positivity': sentiment_analyzer_scores(tweet.full_text)['pos'],
                     'negativity': sentiment_analyzer_scores(tweet.full_text)['neg']
                     }
        tweets_list.append(tweet_dict)
        
    # input created csv into pandas and return as DataFrame
    data = load_data(tweets_list)
    return data


def main():
    api = api_setup()
    # verify my credentials
    try:
        api.verify_credentials()
        st.write("Authentication verified.")
    except:
        st.write("Error during authentication.")
        
    data = get_user_tweets(api, 'earny_joe')
    if checkbox('Raw Data?'):
        st.write(data)


main()