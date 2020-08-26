import re
import requests


class cleanTweets():
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               #u"\U0001F170-\U00015251"  # This should be enclosed charachters like red B Gives me an error rip
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    def __init__(self):
       pass

    def remove_emoji(self,tweet):
        return self.emoji_pattern.sub(r'', tweet)

    def get_emoji(self,tweet):
        return re.findall(self.emoji_pattern,tweet)

    def clean_tweet(self,tweet):
        tweet = re.sub(r'http\S+\s*', '', tweet)  # remove URLs
        
        tweet = re.sub(r'RT|cc', '', tweet)  # remove RT and cc

        # tweet = re.sub(r'#\S+', '', tweet)  # remove hashtags


        # tweet = re.sub(r'@\S+', '', tweet)  # remove mentions # This removes all mentions, want to remove the first one if its there, but like the retweet one, not one that would make the text look weird
        tweet = re.sub(r'[%s]' % re.escape(r"""!"$%&'()*+,-./:;<=>?'[\]^_`@{|}~"""), ' ', tweet)  # remove punctuations// iF YOU comment out mentions make sure to take out the '@' symbol from here
        tweet = re.sub(r'\s+', ' ', tweet)  # remove extra whitespace
        tweet = " ".join(tweet.split()) # Removes all newline and tab charachters in the text 
        return tweet
    
    def getExternalLinks(self,tweet):
        return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet)

    def unshorten_url(self,url):
        return requests.head(url, allow_redirects=True).url
    
    def removeLastHashtag(self,tweet):
        *beginnning, last = tweet.split()
        if ("#" in last):
            tweet = ' '.join(beginnning)
            self.removeLastHashtag(tweet)
        else:
            return tweet
    
    def removeFirstMention(self,tweet):
        pass

        




