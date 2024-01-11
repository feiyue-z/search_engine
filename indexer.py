import json
import re
import os
from bs4 import BeautifulSoup
import datetime
from nltk.stem import PorterStemmer

# paritition design example
# {"uci":
#     "df": 100,
#     "post": {
#         0: 3,
#         2: 5,
#         6: 2,
#         ...
#     },
# }
# uci = term
# df = document frequency
# 0: 3 = docId: term frequency (occurence in a single document w/o log())

docId = 0
webpage = {}

posting = {}
postingCount = 0

partitionId = 0
PARTITION_SIZE = 8000000

def start(path):
    for folder in os.listdir(path):
        dir = os.path.join(path, folder)
        if os.path.isdir(dir):
            for file in os.listdir(dir):
                fileDir = os.path.join(dir, file)
                process_file(fileDir)

def process_file(file):
    global docId
    
    fin = open(file, 'r')
    dict = json.load(fin)
    fin.close()

    url = dict['url']
    if url not in webpage:
        webpage[docId] = url

        soup = BeautifulSoup(dict['content'], 'html.parser')
        importantWords = get_important_words(soup)
        
        tokens = tokenizer(soup.text)
        tokens = stemmer(tokens)
        index(tokens, docId, importantWords)
        docId += 1

        print(docId)
 
def tokenizer(text):
    tokens = []
    tokens += re.split('[^A-Za-z0-9]+', text.lower())

    # filter() tests if each element of a sequence true or not
    # and returns a filtered iterator
    # here, it removes None from tokens
    ret = list(filter(None, tokens))
    return ret

def stemmer(tokens):
    ps = PorterStemmer()
    ret = [ps.stem(token) for token in tokens]
    return ret

def get_important_words(soup):
    result = soup.find_all(['title', 'bold', 'h1', 'h2', 'h3'])
    str = ''
    for each in result:
        str += each.text + ' '
    return tokenizer(str)

def index(tokens, id, importantWords):
    global postingCount

    for token in tokens:
        if token in posting:
            if id not in posting[token]['post']:
                posting[token]['df'] += 1
                if token in importantWords:
                    posting[token]['post'][id] = [1, True]
                else:
                    posting[token]['post'][id] = [1, False]
            else:
                posting[token]['post'][id][0] += 1
        else:
            posting[token] = {}
            posting[token]['df'] = 1
            if token in importantWords:
                posting[token]['post'] = {id: [1, True]}
            else:
                posting[token]['post'] = {id: [1, False]}

        postingCount += 1
        if postingCount >= PARTITION_SIZE:
            dump()
            
def dump():
    global partitionId, postingCount, posting

    fpost = open('partitions/posting{}.json'.format(partitionId), 'w+')
    fidx = open('partitions/idx{}.json'.format(partitionId), 'w+')

    idx = {}
    line = 0
    posting = sorted(posting.items(), key=lambda x:x[0])

    for each in posting:
        pos = fpost.tell()
        idx[line] = pos
        json.dump(each, fpost)
        fpost.write('\n')
        line += 1

    fpost.close()
    json.dump(idx, fidx)
    fidx.close()

    posting = {}
    postingCount = 0
    partitionId += 1

if __name__ == '__main__':
    startDate = datetime.datetime.now()

    path = 'ANALYST'
    start(path)

    if len(posting) != 0:
        dump()

    fout = open('webpage.json', 'w+')
    json.dump(webpage, fout)
    fout.close()

    endDate = datetime.datetime.now()

    print("start date: {}".format(startDate))
    print("end date: {}".format(endDate))
