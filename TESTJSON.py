import tweepy
import backend_config as config
import json
from tweepy.parsers import JSONParser


consumer_key = config.Twitter['Consumer_Key']
consumer_secret = config.Twitter['Consumer_Secret']
access_token = config.Twitter['Access_Token']
access_token_secret = config.Twitter['Access_Secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=JSONParser())

searchParameters = ['Trump']

results = api.search(q=searchParameters)
json_str = json.dumps( results )

print(json_str)
