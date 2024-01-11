import json
import os
import math
import datetime

NUM_PARTITION = 8

def get_partition_size():
    ret = []
    for i in range(NUM_PARTITION):
        file = 'partitions/posting{}.json'.format(i)
        with open(file) as f:
            count = sum(1 for _ in f)
        ret.append(count)
    return ret

def merge():
    sizes = get_partition_size()
    pointers = [0] * NUM_PARTITION
    mergedFile = open('merge/merged.txt', 'w+')
    masterIndex = {}

    while True:
        print(pointers)
        if all(pt >= sizes[i] for i, pt in enumerate(pointers)) == True:
            break

        chunks = {}
        for i in range(NUM_PARTITION):
            if pointers[i] >= sizes[i]:
                continue

            fpost = open('partitions/posting{}.json'.format(i), 'r')
            fidx = open('partitions/idx{}.json'.format(i), 'r')

            idx = json.load(fidx)
            fpost.seek(idx[str(pointers[i])])
            chunks[i] = json.loads(fpost.readline())

            fpost.close()
            fidx.close()
        
        minTerm = '{'
        for posting in chunks.values():
            if posting[0] < minTerm:
                minTerm = posting[0]

        print(minTerm)

        mergedPosting = {}
        mergedDf = 0
        for id, posting in chunks.items():
            if posting[0] == minTerm:
                mergedDf += posting[1]['df']
                mergedPosting.update(posting[1]['post'])
                pointers[id] += 1

        update_tfidf(mergedDf, mergedPosting)

        masterIndex[minTerm] = mergedFile.tell()
        mergedFile.write(json.dumps(mergedPosting) + '\n')

    mergedFile.close()

    with open('merge/master_index.json', 'w+') as fout:
        json.dump(masterIndex, fout)

def update_tfidf(df, posting):
    for key, value in posting.items():
        isImportant = value[1]
        # value is now tf-idf, instead of [occurence, isImportant]
        posting[key] = (1 + math.log(value[0])) * math.log(N/df, 10)
        # add weight for important words
        if isImportant == True:
            posting[key] *= 10

# N, count of corpus
def get_N():
    with open('webpage.json', 'r') as fin:
        webpage = json.load(fin)
    return len(webpage)

if __name__ == '__main__':
    startDate = datetime.datetime.now()

    N = get_N()
    merge()

    endDate = datetime.datetime.now()
    
    print("start date: {}".format(startDate))
    print("end date: {}".format(endDate))
