from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer 

import json
import os
import math
import operator

NUM_FILES = 3

stop_words = set(stopwords.words('spanish')) 
ps = PorterStemmer()

def preprocessing(input):
    word_tokens = word_tokenize(input)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    output = []
    for w  in filtered_sentence:
        output.append(ps.stem(w))
    return output

def func_tf(tf):
    return (math.log(1+tf,10))

def func_idf (N,df):
    return math.log(N/df,10)

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
                    idfromfile = newTweet.id
                    #print (newTweet.__dict__)
                    word_tokens = word_tokenize (TweetText ['text'])
                    filtered_sentence = [w for w in word_tokens if not w in stop_words]
                    for word in filtered_sentence:
                        word = ps.stem (word)
                        if not (word in self.words):
                            self.words [word] = {}
                        if idfromfile in list(self.words [word].keys()):
                            tempWord = Word (self.words [word] [idfromfile] ['cant'], self.words [word] [idfromfile] ['idFile'])
                            tempWord.ind = self.words [word] [idfromfile] ['ind']
                            tempWord.cant += 1
                            self.words [word] [idfromfile] = tempWord.__dict__
                        else:
                            newWord = Word (1, newTweet.file)
                            newWord.ind = ind
                            self.words [word] [idfromfile] = newWord.__dict__

                    ind += 1
            self.numtweets += ind
            num += 1
            print ("listo\n")
            if (num > 3):
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
    query_tfidf = {}
    docs_cosine = {}
    doc_tfidf = {}
    qi2 = 1
    di2 = {}
    dataTweets = {}
    text = preprocessing(query)
    with open('index.json','r') as jsonfile:
        content = jsonfile.read()
    data = json.loads (content)
    for word in text:
        if word in list(data.keys()):
            if word in list(query_tfidf.keys()):
                query_tfidf[word] += 1
            else:
                query_tfidf[word] = 1
    for word in list(query_tfidf.keys()):
        #For query
        query_tfidf[word] = func_tf(query_tfidf[word])
        query_tfidf[word] = query_tfidf[word] * func_idf(NUM_FILES,len(data[word]))

        qi2  += math.pow (query_tfidf[word], 2)
        #For docs
        doc_tfidf [word] = {}
        for doc in list (data [word].keys()):
            doc_tfidf [word] [doc] = func_tf(data [word] [doc]['cant']) *func_idf(NUM_FILES,len(data[word]))
            if doc in list(di2.keys()):
                di2[doc] += math.pow (doc_tfidf [word][doc], 2)
            else:
                di2[doc] = math.pow (doc_tfidf [word][doc], 2)

            if doc in docs_cosine:
                docs_cosine [doc] += doc_tfidf [word] [doc] * query_tfidf [word]
            else:
                docs_cosine [doc] = doc_tfidf [word] [doc] * query_tfidf [word]
                dataTweets [doc] = [data[word][doc]['ind'], data[word][doc]['idFile']]

    for ans in list (docs_cosine):
        docs_cosine [ans] = docs_cosine [ans] / math.sqrt(qi2 * di2[ans])
        
        
    resultado = sorted(docs_cosine.items(), key = operator.itemgetter(1), reverse=True)
    #print (docs_cosine)
    max = 1
    for key in resultado:
        print ("\n",max, " result:\n" )
        printTweet (dataTweets [key[0]][1], key[0], dataTweets [key[0]][0])
        max = max + 1
        if (max > 10):
            break

    print (len(docs_cosine))

            #for key in data [word]:
             #   printTweet (key, data[word] [key] ['idFile'], data [word] [key] ['ind'])

def printTweet (file, id, index):
    with open ('parse/' + file, 'r') as jsonfile:
        content = jsonfile.read ()
    data = json.loads (content)
    print (data [index]['id'])
    print (id)
    if (str(data [index]['id']) == str(id) ):
        for key in data [index]:
            print (key, " : ", data [index] [key])
        print ("---------")
    else:
        print("error")
        print(data [index] ['id'], id, index)


print("****************")

inver = InvertedIndex ()
#inver.tokenize ()

print ("****************")
#inver.printlist ()

#inver.index ()

while (True):
    tosearch = input ("Search :...  ")
    search (tosearch)
#inver.printlist ()
