from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer 

import json
import os

stop_words = set(stopwords.words('spanish')) 
ps = PorterStemmer()

def preprocessing(input):
    word_tokens = word_tokenize(input)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    output = []
    for w  in filtered_sentence:
        output.append(ps.stem(w))
    return output

class InvertedIndex: 
    def __init__(self):
        self.words = {}
        self.numtweets = 0
        self.filesnum = 0

    def tokenize (self):
        num = 0
        for file in os.listdir (os.getcwd () + '/parse'):
            with open ('parse/' + file) as jsonfile:
                data = json.load (jsonfile)
                ind = 0
                for TweetText in data:
                    word_tokens = word_tokenize (TweetText ['text'])
                    filtered_sentence = [w for w in word_tokens if not w in stop_words]
                    for word in filtered_sentence:
                        word = ps.stem (word)
                        if not (word in self.words):
                            self.words [word] = {}
                        if (file + str (ind)) in self.words [word]:
                            self.words [word] [file + str (ind)] += 1
                        else:
                            self.words [word] [file + str (ind)] = 1

                    ind += 1
            self.numtweets += ind
            num += 1
            print ("listo\n")
        self.filesnum = num

    def printlist (self):
        for key in self.words:
            print (key, " : ", self.words[key])
        print ("Hay " + str(len (self.words)) + " palabras")
        print ("Hay " + str(self.numtweets) + " tweets")
        print ("Hay " + str(self.filesnum) + " tweets")

    def index (self):
        with open('index.json', 'w') as jsonfile:
            for key in self.words:
                data = {}
                data[key] = []
                data[key].append({
                    'location' : self.words[key]
                })
                json.dump(data,jsonfile)




text = "this is an example of the preprocessing done"

test = preprocessing(text)

print("****************")

inver = InvertedIndex ()
inver.tokenize ()
inver.index ()
#inver.printlist ()