# Search Engine
## Description
This is a milestone project for Information Retrieval course.<br>
The search engine is composed of three parts:
* indexer - turning scraped webpages into (partitioned) inverted indices
* merger - merging partitions into a master index file and a complete inverted index table with tf-idf scores
* retriever - handling user query by finding relevant websites in the merged index file
## Getting Started
Before you start, make sure `nltk` is installed.
Run the line below if you haven't already installed the package:
```
pip3 install nltk
```
## Usage
### Step 1
Run indexer. Note `\DEV` is where scraped webpages are stored and partitions will output in `\partitions`.
```
python3 indexer.py
```
### Step 2
Run merger to put all partitions together by generating a massive `merged.txt` and a master index `master_index.json` that keeps track of the byte position of all entries for quick look-up.
```
python3 merger.py
```
### Step 3
Run retriever.
```
python3 retriever.py
```
