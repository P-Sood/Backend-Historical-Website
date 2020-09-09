import tweepy
import backend_config as config
import json
import sys
consumer_key = config.Twitter['Consumer_Key']
consumer_secret = config.Twitter['Consumer_Secret']
access_token = config.Twitter['Access_Token']
access_token_secret = config.Twitter['Access_Secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token,access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
#status = api.search_full_archive(environment_name = "fullArchiveSearch", query = "#Trump" ,fromDate = "2017-09-02".replace("-","") + "1201", toDate = "2017-09-06".replace("-","") + "1159", maxResults  = 100)
status = api.search(q = ["#Trump"],count= 20 ,lang="en",since = "2020-09-02", until = "2020-09-06" ,tweet_mode="extended")
#status = api.user_timeline(user="ishansood44", count=1)[0]
#JSON = json.dumps(status)
#sys.stdout = open("some.txt", "w")
#print(JSON)
#sys.stdout.close()
#print(len(status))
