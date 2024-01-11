import re
import json
import datetime
from nltk.stem import PorterStemmer

webpage = {}
masterIndex = {}
mergedFile = None

def tokenizer(text):
    tokens = []
    tokens += re.split('[^A-Za-z0-9]+', text.lower())
    ret = list(filter(None, tokens))
    return ret

def stemmer(tokens):
    ps = PorterStemmer()
    ret = [ps.stem(token) for token in tokens]
    return ret

def load_files():
    global webpage, masterIndex, mergedFile

    file = 'webpage.json'
    fin = open(file, 'r')
    webpage = json.load(fin)
    fin.close()

    file = 'merge/master_index.json'
    fin = open(file, 'r')
    masterIndex = json.load(fin)
    fin.close()

    file = 'merge/merged.txt'
    mergedFile = open(file, 'r')

def search(query):
    global mergedFile
    
    match = []
    for term in query:
        if term in masterIndex:
            bytePos = masterIndex[term]
            mergedFile.seek(bytePos)
            posting = json.loads(mergedFile.readline())
            match.append(posting)

    intersect = set(match[0].keys())
    for posting in match:
        intersect = intersect.intersection(posting.keys())
    
    result = {}
    for posting in match:
        for docId, score in posting.items():
            if docId in intersect:
                if docId in result:
                    result[docId] += score
                else:
                    result[docId] = score
    
    if len(result) != 0:
        for docId, score in sorted(result.items(), key=lambda x:x[1], reverse=True):
            print('> {}'.format(webpage[docId]))
        print("> END OF SEARCH")
    else:
        print("> NO RESULT FOUND")

if __name__ == '__main__':
    load_files()
    query = input("NEW SEARCH > ")
    start_date = datetime.datetime.now()

    tokens = tokenizer(query)
    tokens = stemmer(tokens)
    terms = list(set(tokens)) # to remove duplicates
    search(terms)

    end_date = datetime.datetime.now()
    mergedFile.close()
    print('time used: {}ms'.format((end_date - start_date).total_seconds() * 1000))
