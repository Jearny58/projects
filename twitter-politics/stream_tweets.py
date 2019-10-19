from joetools import private
from textblob import TextBlob
import sqlite3
import dataset
import tweepy
import time

# setup tweepy to authenticate with Twitter with the following code
auth = tweepy.OAuthHandler(private.TWITTER_APP_KEY, private.TWITTER_APP_SECRET)
auth.set_access_token(private.TWITTER_KEY, private.TWITTER_SECRET)
# create an API object to pull data from Twitter, pass in the authentication from above
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
print('API Set-up!')

# connect to database
db = dataset.connect(private.CONNECTION_STRING)
print('Database connected; defining MyStreamListener')

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if status.retweeted:
            return

        description = status.user.description
        loc = status.user.location
        text = status.text
        coords = status.coordinates
        geo = status.geo
        name = status.user.screen_name
        user_created = status.user.created_at
        followers = status.user.followers_count
        id_str = status.id_str
        created = status.created_at
        retweets = status.retweet_count
        bg_color = status.user.profile_background_color
        blob = TextBlob(text)
        sent = blob.sentiment

        if geo is not None:
            geo = json.dumps(geo)

        if coords is not None:
            coords = json.dumps(coords)

        table = db[private.TABLE_NAME]
        try:
            table.insert(dict(
                user_description=description,
                user_location=loc,
                coordinates=coords,
                text=text,
                geo=geo,
                user_name=name,
                user_created=user_created,
                user_followers=followers,
                id_str=id_str,
                created=created,
                retweet_count=retweets,
                user_bg_color=bg_color,
                polarity=sent.polarity,
                subjectivity=sent.subjectivity,
            ))
        except ProgrammingError as err:
            print(err)

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False

if __name__ == "__main__":
    db = dataset.connect(private.CONNECTION_STRING)
    print('Database connected; defining MyStreamListener')
    # setup tweepy to authenticate with Twitter with the following code
    auth = tweepy.OAuthHandler(private.TWITTER_APP_KEY, private.TWITTER_APP_SECRET)
    auth.set_access_token(private.TWITTER_KEY, private.TWITTER_SECRET)
    # create an API object to pull data from Twitter, pass in the authentication from above
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    print('API Set-up!')
    stream_listener = MyStreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=private.TRACK_TERMS)
    time.sleep(5)
    stream.disconnect()