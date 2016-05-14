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
if len(sys.argv)==1:
   print ("Syntax: index.py <collection>")
   exit(0)
collection = sys.argv[1]

if not os.path.isdir(collection):
    print("Collection", collection, "not found.")
    exit(0)

titles = {}
data = {}

filenames = glob.glob(collection + "/document.*") # Get list of filenames
for f in filenames: # Store the title and contents of every file into the titles and data dictionary
    title = f[f.find("/")+1:]
    docNo = f[f.find(".")+1:]

    contents = open(f, "r", encoding='utf-8', errors='ignore')
    titles[docNo] = title
    data[docNo] = contents.read().replace('\n',' ')
    contents.close()

# document length/title file
g = open (collection + "_index_len", "w")

# create inverted files in memory and save titles/N to file
index = {}
brf_index = {}
N = len (data.keys())
p = porter.PorterStemmer ()
for key in data:
    content = re.sub (r'[^ a-zA-Z0-9]', ' ', data[key])
    content = re.sub (r'\s+', ' ', content)
    words = content.split (' ')
    doc_length = 0
    for word in words:
        if word != '':
            if parameters.stemming:
                word = p.stem (word, 0, len(word)-1)
            doc_length += 1
            if not word in index:
                index[word] = {key:1}
            else:
                if not key in index[word]:
                    index[word][key] = 1
                else:
                    index[word][key] += 1
            if not key in brf_index:
                brf_index[key] = {word:1}
            else:
                if not word in brf_index[key]:
                    brf_index[key][word] = 1
                else:
                    brf_index[key][word] += 1
    print (key, doc_length, titles[key], sep=':', file=g)

# document length/title file
g.close ()

# write inverted index to files
try:
   os.mkdir (collection+"_index")
except:
   pass
for key, value in index.items():
    f = open (collection+"_index/"+key, "w")
    for entry, entry_value in value.items():
        print (entry, entry_value, sep=':', file=f)
    f.close ()

# write brf index to files
try:
   os.mkdir (collection+"_brf_index")
except:
   pass
for key, value in brf_index.items():
    brf_file = open (collection+"_brf_index/"+"word_count"+"."+key,"w")
    for entry, entry_value in value.items():
        print (entry, entry_value, sep=':', file=brf_file)
    brf_file.close()
