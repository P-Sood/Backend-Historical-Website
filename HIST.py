import tweepy
import re
import csv
import os
from datetime import date
import json

import sys



from database import DataBase
from cleanTweets import cleanTweets

from wordFrequency import wordFrequency
import backend_config as config


from urllib.parse import urlparse

# Tweepy and Twurl tweet JSON format is different
# Tweepy and Twurl have the same attributes you just get them differently
# Tweepy uses dot method and Twurl uses indexing 

    
class TwitterAPITweepy(cleanTweets,DataBase):
    
    def __init__(self,consumer_key,consumer_secret,access_token,access_token_secret,database):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.database = database


    def Auth(self):
        try:
            self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
            self.auth.set_access_token(self.access_token, self.access_token_secret)
            self.api = tweepy.API(self.auth,wait_on_rate_limit=True)
        except tweepy.error.TweepError:
            print("Something is wrong with one of your keys from Twitter")    
        try:
            self.database.connection()
        except:
            print("Something is wrong with one of your keys from MongoDB") 

        # if you add terms to the searchParams list, it will use the logical and gate
    def HIST(self,csvFileName, searchParameters , since = "2020-01-01" , until = str(date.today()), count = 5):

        self.Auth()
        
        lenSearch = len(searchParameters)
    
        csvFile = open(csvFileName, 'w',encoding="utf-8",newline="")
        fieldnames = ['_id','user_id','date','is_retweet','is_thread','text','emoji','media','likes','retweets','related_hashtags','external_links','tweet_link','search_term']
        writer = csv.DictWriter(csvFile,fieldnames=fieldnames) 
        writer.writeheader()

        query = []
        for i in range(lenSearch):
            query.append(searchParameters[i].lower())

        # If you want to add another field to the csv file, follow code below and then put it in fieldnames as well 
        #for tweet in tweepy.Cursor(self.api.search_full_archive,environment_name = "fullArchive",query = searchParameters_1,fromDate = since.replace("-","") + "1201", toDate = until.replace("-","") + "1159"  ).items(10):
        #    print(tweet)

        for  tweet in tweepy.Cursor(self.api.search_full_archive,environment_name = "fullArchiveSearch",query = searchParameters,fromDate = since.replace("-","") + "1201", toDate = until.replace("-","") + "1159", maxResults = 100  ).items(100):
            user =  tweet.user
            imgTag = ""
            # Making sure there is no link and then adding keys to my dictionary with specific values to be written to csv            
            parsed_tweet = {
                '_id':  tweet.id_str,
                'user_id':  user.screen_name,
                'date': str(tweet.created_at),
                'related_hashtags': [],
                'external_links': [],
                'search_term': searchParameters,
                'media' : "",
                }

                # parsed_tweet['text'] = super().remove_emoji(super().clean_tweet(tweet['extended_tweet']['full_text'])

            try:
                parsed_tweet['emoji']: super().get_emoji(tweet.extended_tweet['full_text'])
            except:
                parsed_tweet['emoji']: super().get_emoji(tweet.text)


            if hasattr(tweet, "retweeted_status"):  # Check if Retweet
                try:
                    parsed_tweet['text'] = super().clean_tweet(super().remove_emoji(tweet.retweeted_status.extended_tweet["full_text"])).strip()
                except:
                    parsed_tweet['text'] = super().clean_tweet(super().remove_emoji(tweet.retweeted_status.text)).strip()
            else:
                try:
                    parsed_tweet['text'] = super().clean_tweet(super().remove_emoji(tweet.extended_tweet["full_text"])).strip()
                except:
                    parsed_tweet['text'] = super().clean_tweet(super().remove_emoji(tweet.text)).strip()
                    

            # With 240 max characters, this loop is O(120) // 120 number symbol characters and 120 alphanumeric characters that are the hashtag
            # In actuality max is like 10, but not every tweet has it
            try:
                for hashtag in tweet.retweeted_status.extended_tweet['entities']['hashtags']:
                    related_hashtags = "#" + hashtag['text']
                    if (related_hashtags.lower() not in query):
                        parsed_tweet['related_hashtags'].append(related_hashtags)
            except:
                try:
                    for hashtag in tweet.extended_tweet['entities']['hashtags']:
                        related_hashtags = "#" + hashtag['text']
                        if (related_hashtags.lower() not in query):
                            parsed_tweet['related_hashtags'].append(related_hashtags)
                except:
                    for hashtag in tweet.entities['hashtags']:
                        related_hashtags = "#" + hashtag['text']
                        if (related_hashtags.lower() not in query):
                            parsed_tweet['related_hashtags'].append(related_hashtags)

            try:
                if (tweet.retweeted_status.in_reply_to_status_id == None):
                    parsed_tweet['is_thread'] = "False"
                else:
                    parsed_tweet['is_thread'] = "True"
            except:
                if (tweet.in_reply_to_status_id == None):
                    parsed_tweet['is_thread'] = "False"
                else:
                    parsed_tweet['is_thread'] = "True"
            

            # The retweeted tweet has the actual likes of the tweet, tweets that are retweets usually have 0 likes and hold no info
            # links are just links that the user puts inside of their text, used regex to find it
            try:
                parsed_tweet['likes'] = str(tweet.retweeted_status.favorite_count) 
                parsed_tweet['tweet_link'] = "https://twitter.com/id/status/" + tweet.id_str 
                parsed_tweet['retweets'] =  str(tweet.retweeted_status.retweet_count) 

                parsed_tweet['is_retweet'] = "True"
            except:
                parsed_tweet['likes'] =  str(tweet.favorite_count) 
                parsed_tweet['tweet_link'] = "https://twitter.com/id/status/" + tweet.id_str 
                parsed_tweet['retweets'] =  str(tweet.retweet_count) 

                parsed_tweet['is_retweet'] = "False"

            try:
                for link in tweet.retweeted_status.extended_tweet['entities']['urls']:
                    if "twitter.com" not in link['display_url']:
                        parsed_tweet['external_links'].append(link['expanded_url'])
            except:
                try:
                    for link in tweet.retweeted_status.entities['urls']:
                        if "twitter.com" not in link['display_url']:
                            parsed_tweet['external_links'].append(link['expanded_url'])
                except:
                    try:
                        for link in tweet.extended_tweet['entities']['urls']:
                            if "twitter.com" not in link['display_url']:
                                parsed_tweet['external_links'].append(link['expanded_url'])
                    except:
                        for link in tweet.entities['urls']:
                            if "twitter.com" not in link['display_url']:
                                parsed_tweet['external_links'].append(link['expanded_url'])
    
            try:
                # For retweet of video/multiple images
                media_retweet = tweet.retweeted_status.extended_tweet['entities']['media']
                if media_retweet[0]['type'] == "video":
                    parsed_tweet['media'] = media_retweet[0]['media_url']
                else:
                    for image in media_retweet:
                        imgTag += " " + image['media_url']
                    parsed_tweet['media'] = imgTag
            except:
                try:
                    # For tweet of video/multiple images
                    media_tweet = tweet.extended_tweet['entities']['media']
                    if media_tweet[0]['type'] == "video":
                        parsed_tweet['media'] =  media_tweet[0]['media_url']
                    else:
                        for image in media_tweet:
                            imgTag += image['media_url']
                        parsed_tweet['media'] = imgTag
                except:
                    try:
                        # For one picture
                        parsed_tweet['media'] = tweet.entities['media'][0]['media_url']
                    except:
                        parsed_tweet['media'] = ""

            # #self.database.insert_one(parsed_tweet)
            writer.writerow(parsed_tweet)
            # #print(tweet)
          

def main():
    consumer_key = config.Twitter['Consumer_Key']
    consumer_secret = config.Twitter['Consumer_Secret']
    access_token = config.Twitter['Access_Token']
    access_token_secret = config.Twitter['Access_Secret']

    UserName = config.MongoDB['UserName']
    Password = config.MongoDB['Password']
    database = config.MongoDB['Database']
    collection = config.MongoDB['Collection']

    mongoDB = DataBase(UserName,Password,database,collection)

    # When searching for multiple hashtags we can do 'OR' using "#THIS OR #THAT"
    # When searching for multiple hashtags we can do 'AND' using "#This #That"

    api = TwitterAPITweepy(consumer_key,consumer_secret,access_token,access_token_secret,mongoDB)
    api.HIST(csvFileName= "TrumpCSV_5.csv",searchParameters="#Trump OR #Cat", since = "2017-09-02", until = "2017-09-06")

    #wordFreq = wordFrequency()
    #wordFreq.getWordFreq_toText(textFileName = "WordCount" + search + ".txt" , csvFileName = "tweets_1" + search + ".csv", collectionWords = ["portland"])

if __name__ == "__main__":
    main()
