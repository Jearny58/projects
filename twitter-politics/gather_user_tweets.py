# import libraries
import dataset
import logging
from joetools import private
import os
import tweepy
import pandas as pd

# set up logger
logger = logging.getLogger()

# sets environment variables
private.environment_variables()

# define necessary functions
def database_connect():
    '''connects to PostgreSQL database and table (via user input)'''
    table_name = str(input('Please insert table name you would like to reference: '))
    
    try:
        # connect to PostgreSQL database
        db = dataset.connect(os.environ.get('CONNECTION_STRING'))
        # create reference to specified table
        table = db.create_table(table_name, primary_id='tweet_id', primary_type=db.types.text)
        return table
    except Exception as e:
        print(e)


def api_setup():
    '''sets up Twitter API'''
    # access tweepy authenticator
    auth = tweepy.OAuthHandler(os.environ.get('TWITTER_API_KEY'), os.environ.get('TWITTER_API_SECRET'))
    auth.set_access_token(os.environ.get('TWITTER_TOKEN'), os.environ.get('TWITTER_TOKEN_SECRET'))

    # pass in above authentication to API
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error('Error creating API', exc_info=True)
        raise e
    logger.info('API created')
    
    return api


def number_tweets():
    while True:
        amount = input("Enter number of tweets you'd like to gather: ")
        try:
            num_tweets = int(amount)
            if num_tweets >= 0 and num_tweets <= 3200:
                break
            else:
                print("Number of tweets must be between 0 and 3,200. Please try again.")
        except ValueError:
            print("Amount must be a number, try again")
    return num_tweets


def get_username(api):
    '''takes user input and assigns to username if it exists'''
    while True:
        username = str(input("Enter username of Twitter account: "))
        try:
            if api.get_user(screen_name=username):
                break
        except Exception:
            print('Please enter a valid username.')
    return username


def gather_tweets(api, username, num_tweets, table):
    '''function that gathers tweets from specified username, and inserts into specified table'''
    # insert database table reference
    table = table
    
    for tweet in tweepy.Cursor(api.user_timeline, id=username, tweet_mode='extended').items(num_tweets):
        # retrieve tweet_id from tweet
        tweet_id = tweet.id_str    
        if table.find_one(tweet_id=tweet_id) is not None:
            pass
        else:
            created_at = tweet.created_at
            source = tweet.source
            retweet_count = tweet.retweet_count
            favorite_count = tweet.favorite_count
            if tweet.entities['hashtags']:
                hashtags = [n['text'] for n in tweet.entities['hashtags']]
            else:
                hashtags = 'None' 
            if tweet.entities['urls']:
                urls = [n['url'] for n in tweet.entities['urls']]
            else:
                urls = 'None'    
            text = tweet.full_text

            # try to insert
            try:
                table.upsert(dict(
                    tweet_id=tweet_id,
                    created_at=created_at,
                    source=source,
                    retweet_count=retweet_count,
                    favorite_count=favorite_count,
                    hashtags=hashtags,
                    urls=urls,
                    text=text), keys=['tweet_id'])
                print('Tweet ID {} from {} inserted in table.'.format(tweet_id, str(created_at)))
            except Exception as e:
                print(e)


# define main program                
def main():
    table = database_connect()
    api = api_setup()
    username = get_username(api)
    num_tweets = number_tweets()
    gather_tweets(api, username, num_tweets, table)
    

    
# run main program
main()
    
    
