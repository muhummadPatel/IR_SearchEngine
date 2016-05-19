# Simple extended boolean search engine: indexer based on cranfield format
# Hussein Suleman
# 21 April 2016
import glob
import os
import re
import sys

import parameters
import porter

# check parameter for collection name
if len(sys.argv) == 1:
    print("Syntax: index.py <collection>")
    exit(0)
collection = sys.argv[1]

if not os.path.isdir(collection):
    print("Collection", collection, "not found.")
    exit(0)

titles = {}
data = {}

filenames = glob.glob(collection + "/document.*")  # Get list of filenames
for f in filenames:  # Store the title and contents of every file into the titles and data dictionary
    title = f[f.find("/") + 1:]
    docNo = f[f.find(".") + 1:]

    contents = open(f, "r", encoding='utf-8', errors='ignore')
    titles[docNo] = title
    data[docNo] = contents.read().replace('\n', ' ')
    contents.close()

# document length/title file
g = open(collection + "_index_len", "w")

# create inverted files in memory and save titles/N to file
index = {}
brf_index = {}
stemmed_index = {}
stemmed_index_brf_index = {}
N = len(data.keys())
p = porter.PorterStemmer()
for key in data:
    content = re.sub(r'[^ a-zA-Z0-9]', ' ', data[key])
    content = re.sub(r'\s+', ' ', content)
    words = content.split(' ')
    doc_length = 0
    for word in words:
        if word != '':
            stemmed_word = p.stem(word, 0, len(word) - 1)
            doc_length += 1
            if parameters.case_folding:
                word = word.lower()
                stemmed_word = stemmed_word.lower()
            # Non stemmed index
            if word not in index:
                index[word] = {key: 1}
            else:
                if key not in index[word]:
                    index[word][key] = 1
                else:
                    index[word][key] += 1
            if key not in brf_index:
                brf_index[key] = {word: 1}
            else:
                if word not in brf_index[key]:
                    brf_index[key][word] = 1
                else:
                    brf_index[key][word] += 1

            # Stemmed index
            if stemmed_word not in stemmed_index:
                stemmed_index[stemmed_word] = {key: 1}
            else:
                if key not in stemmed_index[stemmed_word]:
                    stemmed_index[stemmed_word][key] = 1
                else:
                    stemmed_index[stemmed_word][key] += 1
            if key not in stemmed_index_brf_index:
                stemmed_index_brf_index[key] = {stemmed_word: 1}
            else:
                if stemmed_word not in stemmed_index_brf_index[key]:
                    stemmed_index_brf_index[key][stemmed_word] = 1
                else:
                    stemmed_index_brf_index[key][stemmed_word] += 1
    print(key, doc_length, titles[key], sep=':', file=g)

# document length/title file
g.close()

# write inverted index to files
try:
    os.mkdir(collection + "_index")
    os.mkdir(collection + "_stemmed_index")
except:
    pass
for key, value in index.items():
    try:
        f = open(collection + "_index/_" + key, "w")
        for entry, entry_value in value.items():
            print(entry, entry_value, sep=':', file=f)
        f.close()

        f_stemmed = open(collection + "_stemmed_index/_" + key, "w")
        for entry, entry_value in value.items():
            print(entry, entry_value, sep=':', file=f_stemmed)
        f_stemmed.close()
    except FileNotFoundError:
        print("_"+key+" couldn't be opened - ignoring")

for key, value in stemmed_index.items():
    try:
        f_stemmed = open(collection + "_stemmed_index/_" + key, "w")
        for entry, entry_value in value.items():
            print(entry, entry_value, sep=':', file=f_stemmed)
        f_stemmed.close()
    except FileNotFoundError:
        print("_"+key+" couldn't be opened - ignoring")



# write brf index to files
try:
    os.mkdir(collection + "_brf_index")
    os.mkdir(collection + "_stemmed_brf_index")
except:
    pass
for key, value in brf_index.items():
    brf_file = open(collection + "_brf_index/" + "word_count" + "." + key, "w")
    for entry, entry_value in value.items():
        print(entry, entry_value, sep=':', file=brf_file)
    brf_file.close()

for key, value in stemmed_index_brf_index.items():
    brf_file = open(collection + "_stemmed_brf_index/" + "word_count" + "." + key, "w")
    for entry, entry_value in value.items():
        print(entry, entry_value, sep=':', file=brf_file)
    brf_file.close()
