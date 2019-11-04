from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer 

import json
import os
import math
import operator

#Usamos estas variables para poder hacer split con todos los files
NUM_FILES = 4
IDFROMII = 0
START = 1 + ((NUM_FILES) * IDFROMII)

stop_words = set(stopwords.words('spanish')) 
ps = PorterStemmer()

#Se hace el preprocesamiento del input, devuelve una lista con las palabras filtradas y pasaron por steming
def preprocessing(input):
    word_tokens = word_tokenize(input)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    output = []
    for w  in filtered_sentence:
        output.append(ps.stem(w))
    return output

#Usamos esta función para hallar el tf para un tweet y un término
def func_tf(tf):
    return (math.log(1+tf,10))

#Función para hallar idf
def func_idf (N,df):
    return math.log(N/df,10)

#Clase tweet con la que ubicamos el nombre del archivo donde se encuentra el Tweet y el id de este
class Tweet:
    def __init__(self, id_, file_name):
        self.id = id_
        self.file = file_name

#Nos sirve para agregar las palabras al inverted index, aca tambien incluimos la posicion del tweet en el archivo
class Word: 
    def __init__(self, cant_, id_file_):
        self.cant = cant_
        self.idFile =id_file_ #Nombre del archivo
        self.ind = 0

#Clase general del inverted index, words equivale al diccionario con todas las palabras.
class InvertedIndex: 
    def __init__(self):
        #Diccionario de words, cantidad de tweets y cantidad de files
        self.words = {}
        self.numtweets = 0
        self.filesnum = 0

    #Esta funcion recorre los archivos, luego los tweets en este y luego las palabras para poder llenar nuestro diccionario
    
    def tokenize (self):
        num = 0
        idfromfile = 0
        for file in os.listdir (os.getcwd () + '/parse'):
            idfromfile += 1
            #Aqui nos aseguramos que empezaremos a contar con el siguiente archivo
            if (idfromfile < NUM_FILES):
                continue
            with open ('parse/' + file) as jsonfile:
                data = json.load (jsonfile)
                ind = 0
                for TweetText in data:
                    newTweet = Tweet (TweetText ['id'], file)
                    idfromfile = newTweet.id
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
            #Salimos cuando hayamos recorrido 4 archivos
            if (num > 3):
                break
        self.filesnum = num

    #Print del diccionario e información sobre este
    def printlist (self):
        for key in self.words:
            print (key, " : ", self.words[key])
        print ("Hay " + str(len (self.words)) + " palabras")
        print ("Hay " + str(self.numtweets) + " tweets")
        print ("Hay " + str(self.filesnum) + " files")

    #Guarda el diccionario en un .json
    def index (self):
        with open('index' + str(IDFROMII) + '.json', 'w') as jsonfile:
            data = {}
            for key in self.words:
                data[key] = self.words[key]
            json.dump(data,jsonfile)

#Pasa una query por el prepocesamiento y usando tf-idf coseno, se imprimen los 10 mejores resultados y se muestran
#la cantidad de resultados totales
def search(query):
    query_tfidf = {}
    docs_cosine = {}
    doc_tfidf = {}
    qi2 = 1
    di2 = {}
    dataTweets = {}
    text = preprocessing(query)
    #SI SE QUIERE CAMBIAR EL .json SE CAMBIA AQUI EL NOMBRE, EN ESTE CASO ESTAMOS TRABAJANDO CON index.json
    with open('index'  +  '.json','r') as jsonfile:
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
    max = 1
    for key in resultado:
        print ("\n",max, " result:\n" )
        printTweet (dataTweets [key[0]][1], key[0], dataTweets [key[0]][0])
        max = max + 1
        if (max > 10):
            break

    print (len(docs_cosine))


#Imprime la información de un tweet, necesitamos el nombre del archivo, el id y el index
def printTweet (file, id, index):
    with open ('parse/' + file, 'r') as jsonfile:
        content = jsonfile.read ()
    data = json.loads (content)
    if (str(data [index]['id']) == str(id) ):
        for key in data [index]:
            print (key, " : ", data [index] [key])
        print ("---------")
    else:
        print("error")
        print(data [index] ['id'], id, index)

#Esta parte comentada es usada para crear los json de los indices invertidos, se crean 14 json.
"""
for i in range (0, 14):
    IDFROMII = i
    print("****************")

    inver = InvertedIndex ()
    inver.tokenize ()
    inver.index ()

    print ("****************")"""
#inver.printlist ()


#bucle para hacer consultas
while (True):
    tosearch = input ("Search ...:  ")
    search (tosearch)
#inver.printlist ()
