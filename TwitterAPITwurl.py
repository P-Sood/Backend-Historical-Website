import re
import csv
import sys
import json
import os
import glob
import pandas as pd
from datetime import date

from database import DataBase
from cleanTweets import cleanTweets


# Instead of creating hella text and csv files by incrementing
# We should delete the file and remake the file  every single time, 
# That way we dont put anything in the users file storage on the websit
# It will make things more succint 
class TwitterAPITwurl(cleanTweets):

    todaysDate = re.sub(r'[%s]' % re.escape(r"-"), '', str(date.today())) + "0000"

    def __init__(self,path,input_directory,output_directory,devEnvironment):
        self.path = path
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.devEnvironment = devEnvironment

        self.next_count = 0
        self.todaysDate = re.sub(r'[%s]' % re.escape(r"-"), '', str(date.today())) + "0000"

    def firstTwurlCMD(self,query,textFileName,csvFileName,lang = "en",maxResults = "100",fromDate = "202001010000" ,toDate = todaysDate):
        os.chdir(os.path.join(self.path,self.input_directory))
        cmd = 'twurl \"/1.1/tweets/search/fullarchive/' + self.devEnvironment + '.json\" -A \"Content-Type: application/json\" -d \'{\"query\":\"' + query + ' lang:' + lang + '\",\"maxResults\":\"' + str(maxResults) + '\",\"fromDate\":\"' + str(fromDate) + '\",\"toDate\":\"' + str(toDate) + '\"}\' > ' + textFileName + ".txt"
        os.system(cmd)
        self.tweets_JSONtoCSV(query,textFileName,csvFileName, lang=lang ,maxResults = maxResults ,fromDate = fromDate ,toDate = toDate)

    # After doing a tweet search in Twurl, you can save it to a text file, and then run this function
    # To put it in a similar format as up above in csv
    def tweets_JSONtoCSV(self,query,textFileName,csvFileName,lang = "en",maxResults = "100",fromDate = "202001010000" ,toDate = todaysDate):
        self.next_count += 1
        # Get Text from the input directory 
        os.chdir(os.path.join(self.path,self.input_directory))
        textFile = open(textFileName + ".txt" , 'r',encoding="utf-8")
        data = json.load(textFile)

        # Put csv in the output directory
        os.chdir(os.path.join(self.path,self.output_directory))
        csvFile = open(csvFileName + ".csv", 'w',encoding="utf-8", newline='')
        fieldnames = ['user_id','date','twitter_id','text','emojis','media','likes','retweets','related_hashtags','external_links','tweet_link','search_term']
        writer = csv.DictWriter(csvFile,fieldnames=fieldnames) 
        writer.writeheader()

        try:
            nextPageRequest = data['next']
        except:
            print("Next is null inside try catch")

        # When you query in twurl the data you get changes based on JSON, so for the for-loop if you are getting erros
        # Just do a print(tweet) and put that in an online JSON parser and then play around with that until you know 
        # what the data you're receiving actually is

        for tweet in data['results']:
            parsed_tweet = {}
            user = tweet['user']

            
            tags = ""
            imgTag = ""
            url_link = ""

            parsed_tweet['user_id'] = user['screen_name']
            parsed_tweet['date'] = str(tweet['created_at']) 
            parsed_tweet['twitter_id'] = tweet['id_str']
            parsed_tweet['tweet_link'] = "https://twitter.com/id/status/" + tweet['id_str']
            parsed_tweet["search_term"] = query


            try:
                parsed_tweet['emojis'] = super().get_emoji(tweet['extended_tweet']['full_text'].encode('utf-8').decode('utf-8'))               
                parsed_tweet['text'] = super().remove_emoji(super().clean_tweet(tweet['extended_tweet']['full_text'].encode('utf-8').decode('utf-8')))               
            except:
                parsed_tweet['text'] = super().remove_emoji(super().clean_tweet(tweet['text'].encode('utf-8').decode('utf-8')))
                parsed_tweet['emojis'] = super().get_emoji(tweet['text'].encode('utf-8').decode('utf-8'))

            try:
                for hashtag in tweet['retweeted_status']['extended_tweet']['entities']['hashtags']:
                    tags +=  "#" + hashtag['text'] + " "
                #tags = re.sub("[^A-Za-z]", " ", tags)
                parsed_tweet['related_hashtags'] = tags
            except:
                try:
                    for hashtag in tweet['extended_tweet']['entities']['hashtags']:
                        tags +=  "#" + hashtag['text'] + " "
                    #tags = re.sub("[^A-Za-z]", " ", tags)
                    parsed_tweet['related_hashtags'] = tags
                except:
                    for hashtag in tweet['entities']['hashtags']:
                        tags += "#" + hashtag['text'] + " "
                    #tags = re.sub("[^A-Za-z]", " ", tags)
                    parsed_tweet['related_hashtags'] = tags

            # Next block of code checks to see if tweet has a video, print link. If not check if tweet has multiple images, print img links, 
            # if not then check if just 1 media image, print img, if nothing then print empty
            try:
                parsed_tweet['media'] = tweet['extended_tweet']['extended_entities']["media"][0]["video_info"]["variants"][0]["url"]
            except:
                try:
                    for image in tweet['extended_tweet']['extended_entities']["media"]:
                        imgTag += image["media_url_https"]+ " "
                    parsed_tweet['media'] = imgTag 
                except:
                    parsed_tweet['media'] = ""
                    # Might be useless in twurl format
                    """
                    try:
                        parsed_tweet['media'] = tweet.entities["media_url_https"]
                    except: 
                        parsed_tweet['media'] = ""
                    """
            # Here i have just gone thru some differences that appear if the tweet is a retweet or not

            try:
                parsed_tweet['retweets'] = tweet['retweeted_status']['retweet_count'] 
                parsed_tweet['likes'] =  str(tweet['retweeted_status']['favorite_count']) 
                # If a retweet, 1 link is to direct back to the original tweet, so i ignored it and started at 1
            except:
                parsed_tweet['retweets'] = str(tweet['retweet_count']) 
                parsed_tweet['likes'] =  str(tweet['favorite_count']) 
                
            
            try:
                listAddedLinks = re.findall(r'http\S+\s*', tweet['retweeted_status']['extended_tweet']['full_text'])
                for i in range(1,len(listAddedLinks)):
                    url_link += listAddedLinks[i]
                parsed_tweet['external_links'] = url_link
            except:
                try:
                    for links in re.findall(r'http\S+\s*', tweet['extended_tweet']['full_text']):
                        url_link += links
                    parsed_tweet['external_links'] = url_link 
                except:
                    for links in re.findall(r'http\S+\s*', tweet['text']):
                        url_link += links
                    parsed_tweet['external_links'] = url_link

            
            writer.writerow(parsed_tweet)
        textFile.close()

        if ( nextPageRequest != None and self.next_count<4):
            # Both file names will be in format 'search'_i.xxx where search is the term we searched and i is number of times we ran it
            textFileName = textFileName[0:len(textFileName)-2] + "_" + str(self.next_count)
            csvFileName = csvFileName[0:len(csvFileName)-2] + "_" + str(self.next_count)
            print("Getting request number " + str(self.next_count) + "\n")
            self.getNextTweets_fromTwurl(query,nextPageRequest,textFileName,csvFileName, lang=lang ,maxResults = maxResults ,fromDate = fromDate ,toDate = toDate)
        else:
            print("We have finished inside if")
            return

    def getNextTweets_fromTwurl(self,query,Next,textFileName,csvFileName,lang = "en",maxResults = "100",fromDate = "202001010000" ,toDate = todaysDate):
        os.chdir(os.path.join(self.path,self.input_directory))
        cmd = 'twurl \"/1.1/tweets/search/fullarchive/' + self.devEnvironment + '.json\" -A \"Content-Type: application/json\" -d \'{\"query\":\"' + query + ' lang:' + lang + '\",\"maxResults\":\"' + str(maxResults) + '\",\"fromDate\":\"' + str(fromDate) + '\",\"toDate\":\"' + str(toDate) + '\",\"next\":' + str(Next) + '}\' > ' + textFileName + ".txt"
        os.system(cmd)
        print("Got request " + str(self.next_count) + " Now going to generate CSV \n" )
        self.tweets_JSONtoCSV(query,textFileName,csvFileName, lang=lang ,maxResults = maxResults ,fromDate = fromDate ,toDate = toDate)
    
    def AppendCSVs(self,combinedFileName,directory,extension):
        os.chdir(directory)
        #find all csv files in the folder
        #use glob pattern matching -> extension = 'csv'
        #save result in list -> all_filenames
        all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
        #print(all_filenames)

        #combine all files in the list
        combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
        #export to csv
        combined_csv.to_csv( combinedFileName, index=False, encoding='utf-8')    

def main():
    Folder = "InputandOutput"
    input_directory = "input"
    output_directory = "output"
    path = os.path.join(os.getcwd(),Folder)
    input_path = os.path.join(path,input_directory)
    output_path = os.path.join(path,output_directory)
    os.makedirs(input_path)
    os.makedirs(output_path)
    
    
    
    search = "#TwitchBlackout"
    twurl = TwitterAPITwurl(path,input_directory,output_directory,"fullArchive")
    # use file names to be #TwitchBlackout_0.txt and then increment the 0 on both
    twurl.firstTwurlCMD(search,textFileName = search + "_0", csvFileName = search + "_0",fromDate="202006010000", toDate= "202007012359")
    #twurl.AppendCSVs("Animal.csv","Test_AppendFunction","csv")

if __name__ == "__main__":
    main()
