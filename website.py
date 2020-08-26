import tweepy
import datetime


def tweetsDjango_database(self,searchParameters , since = "2020-01-01" , until = str(date.today()), count = 2):

    self.Auth()

    lenSearch = len(searchParameters)
    tweets = []
    query = []
    for i in range(lenSearch):
        query.append(searchParameters[i].lower())

    # If you want to add another field to the csv file, follow code below and then put it in fieldnames as well 

    for tweet in tweepy.Cursor(self.api.search,q=searchParameters,count= count,lang="en",since = since, until = until ,tweet_mode="extended",).items():
        user =  tweet.user
        # Making sure there is no link and then adding keys to my dictionary with specific values to be written to csv            
        parsed_tweet = {
            '_id':  tweet.id_str,
            'user_id':  user.screen_name,
            'is_retweet': "False",
            'is_thread': "False",
            'date': str(tweet.created_at),
            'emoji': super().get_emoji(tweet.full_text),
            'related_hashtags': [],
            'external_links': [],
            'search_term': searchParameters,
            }

        if hasattr(tweet, "retweeted_status"):  # Check if Retweet
            try:
                parsed_tweet['text'] = super().clean_tweet(super().remove_emoji(tweet.retweeted_status.extended_tweet["full_text"])).strip()
            except:
                parsed_tweet['text'] = super().clean_tweet(super().remove_emoji(tweet.retweeted_status.full_text)).strip()
        else:
            try:
                parsed_tweet['text'] = super().clean_tweet(super().remove_emoji(tweet.extended_tweet["full_text"])).strip()
            except:
                parsed_tweet['text'] = super().clean_tweet(super().remove_emoji(tweet.full_text)).strip()
                

        # With 240 max characters, this loop is O(120) // 120 number symbol characters and 120 alphanumeric characters that are the hashtag
        # In actuality max is like 10, but not every tweet has it
        try:
            for hashtag in tweet.retweeted_status.entities['hashtags']:
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
        

        # this code is very slow so we can revert it back but this works 100% where it was more 80% but MUCH faster 
        try:
            listAddedLinks = super().getExternalLinks(tweet.retweeted_status.full_text)
            for i in range(len(listAddedLinks)):
                # I get the t.co url and I unshorten it to check if it actually redirects us back to twitter
                # Then i just put that into my list
                url = super().unshorten_url(listAddedLinks[i])
                x = urlparse(url)
                if (x.netloc != "twitter.com"):
                    parsed_tweet['external_links'].append(super().remove_emoji(url.replace('\n',"")))
        except:   
            listAddedLinks = super().getExternalLinks(tweet.full_text)
            for i in range(len(listAddedLinks)):
                parsed_tweet['external_links'].append(super().remove_emoji(listAddedLinks[i].replace('\n',"")))


        # Next block of code checks to see if tweet has a video, print link. If not check if tweet has multiple images, print img links, 
        # if not then check if just 1 media image, print img, if nothing then print empty


        # Something is wrong with this code, even though it was working a while back, So i need to find what underlying issue causes
        # it to not work right now
        try:
            parsed_tweet['media'] = tweet.extended_entities["media"][0]["video_info"]["variants"][0]["url"]
        except:
            try:
                for image in tweet.extended_entities["media"]:
                    imgTag += image["media_url_https"]+ " "
                parsed_tweet['media'] = imgTag 
            except:
                try:
                    parsed_tweet['media'] = tweet.entities["media_url_https"]
                except:
                    parsed_tweet['media'] = ""
        
        newData = data( _id = parsed_tweet['_id'] , user_id = parsed_tweet['user_id'] , date = parsed_tweet['date'][0:10] ,
        
            text = parsed_tweet['text'] , emoji = parsed_tweet['emoji'] , likes = parsed_tweet['likes'] , 
            
            search_term = parsed_tweet['search_term'] )

        newData.save()

        newTweet = Twitter_data( keyData = newData , is_retweet = parsed_tweet['is_retweet'] , is_thread = parsed_tweet['is_thread'] , 
        
            media = parsed_tweet['media'] , retweets = parsed_tweet['retweets'] , related_hashtags = parsed_tweet['related_hashtags'] , 
            
            external_links = parsed_tweet['external_links']  , tweet_link = parsed_tweet['tweet_link'] )
            
        newTweet.save()

    return tweets 