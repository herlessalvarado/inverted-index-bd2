from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize

def preprocessing(input):
    stop_words = set(stopwords.words('english')) 
    word_tokens = word_tokenize(input)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    ps = PorterStemmer()
    output = []
    for each in filtered_sentence:
        output.append(each)
    for w  in filtered_sentence:
        output.append(ps.stem(w))
    return output

text = "this is an example of the preprocessing done"

test = preprocessing(text)

print(test)