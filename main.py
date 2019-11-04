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

class Tweet:
    def __init__(self, id_, file_name):
        self.id = id_
        self.file = file_name

class Word: 
    def __init__(self, cant_, id_file_):
        self.cant = cant_
        self.idFile =id_file_
        self.ind = 0

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
                    newTweet = Tweet (TweetText ['id'], file)
                    #print (newTweet.__dict__)
                    word_tokens = word_tokenize (TweetText ['text'])
                    filtered_sentence = [w for w in word_tokens if not w in stop_words]
                    for word in filtered_sentence:
                        word = ps.stem (word)
                        if not (word in self.words):
                            self.words [word] = {}
                        if file in list(self.words [word].keys()):
                            tempWord = Word (self.words [word] [file] ['cant'], self.words [word] [file] ['idFile'])
                            tempWord.ind = self.words [word] [file] ['ind']
                            tempWord.cant += 1
                            self.words [word] [file] = tempWord.__dict__
                        else:
                            newWord = Word (1, newTweet.id)
                            newWord.ind = ind
                            self.words [word] [file] = newWord.__dict__

                    ind += 1
            self.numtweets += ind
            num += 1
            print ("listo\n")
            if (num > 2):
                break
        self.filesnum = num

    def printlist (self):
        for key in self.words:
            print (key, " : ", self.words[key])
        print ("Hay " + str(len (self.words)) + " palabras")
        print ("Hay " + str(self.numtweets) + " tweets")
        print ("Hay " + str(self.filesnum) + " files")

    def index (self):
        with open('index.json', 'w') as jsonfile:
            data = {}
            for key in self.words:
                data[key] = self.words[key]
            json.dump(data,jsonfile)

def search(query):
    text = preprocessing(query)
    with open('index.json','r') as jsonfile:
        content = jsonfile.read()
    data = json.loads (content)
    for word in text:
        if word in list(data.keys()):
            print (word, "Files : \n")
            for key in data [word]:
                printTweet (key, data[word] [key] ['idFile'], data [word] [key] ['ind'])

def printTweet (file, id, index):
    with open ('parse/' + file, 'r') as jsonfile:
        content = jsonfile.read ()
    data = json.loads (content)
    if (data [index]['id'] == id ):
        for key in data [index]:
            print (key, " : ", data [index] [key])
        print ("---------")
    else:
        print(data [index] ['id'], id, index)




text = "this is an example of the preprocessing done"

test = preprocessing(text)

print("****************")

inver = InvertedIndex ()
#inver.tokenize ()

print ("****************")
#inver.printlist ()

#inver.index ()
search ("caso bueno")
#inver.printlist ()
