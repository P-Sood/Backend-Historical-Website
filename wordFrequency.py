import string 
import pandas as pd
from nltk.corpus import stopwords
import re


class wordFrequency:
    
    def __init__(self):
        pass
    
    def getWordFreq_toText(self,textFileName,csvFileName,collectionWords,col_list = ["text"]):

        stop_words = set(stopwords.words('english'))

        textFile = open(textFileName , 'w',encoding="utf-8",newline="")
        df = pd.read_csv(csvFileName , usecols=col_list)

        # Create an empty dictionary 
        d = dict() 

        # Loop through each line of the file 
        for line in df['text']: 
            
            # Remove the leading spaces and newline character 
            line = line.strip() 
        
            # Convert the characters in line to  
            # lowercase to avoid case mismatch 
            line = line.lower() 
        
            # Remove the punctuation marks from the line 
            line = re.sub(r'[%s]' % re.escape(r"""!"$%&'()*+,-./:;<=>?'‘’“”[\]^_`@{|}~#"""), ' ', line)
        
            # Split the line into words 
            words = line.split(" ") 

            semiUsefulWords = [word for word in words if not word in stop_words]

            usefulWords = [word for word in semiUsefulWords if not word in collectionWords]
        
            # Iterate over each word in line 
            for word in usefulWords: 

                # Make sure each word has more then 1 character
                if (len(word) > 1):
                    # Check if the word is already in dictionary 
                    if word in d: 
                        # Increment count of word by 1 
                        d[word] += 1
                    else: 
                        # Add the word to dictionary with count 1 
                        d[word] = 1
        # Print the contents of dictionary 
        sort_orders = sorted(d.items(), key=lambda x: x[1], reverse=True) 
        for i in sort_orders:
            textFile.write(str(i[0]) + ":" + str(i[1]) + "\n" )