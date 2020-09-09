import backend_config as config
from database import DataBase
from TwitterAPITweepy import TwitterAPITweepy

def main():
    consumer_key = config.Twitter['Consumer_Key']
    consumer_secret = config.Twitter['Consumer_Secret']
    access_token = config.Twitter['Access_Token']
    access_token_secret = config.Twitter['Access_Secret']
    search = "#Portland"

    UserName = config.MongoDB['UserName']
    Password = config.MongoDB['Password']
    database = config.MongoDB['Database']
    collection = config.MongoDB['Collection']

    mongoDB = DataBase(UserName,Password,database,collection)


    api = TwitterAPITweepy(consumer_key,consumer_secret,access_token,access_token_secret,mongoDB)
    api.get_tweets_tweepy(csvFileName = "tweets_" + search + ".csv" , searchParameters = [search],count=2)

    #wordFreq = wordFrequency()
    #wordFreq.getWordFreq_toText(textFileName = "WordCount" + search + ".txt" , csvFileName = "tweets_1" + search + ".csv", collectionWords = ["portland"])

if __name__ == "__main__":
    main()