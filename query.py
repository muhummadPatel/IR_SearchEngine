# Simple extended boolean search engine: query module
# Hussein Suleman
# 14 April 2016

import re
import math
import sys
import os

import porter
import parameters
import glob

def clean_query(query):
    # clean query
    if parameters.case_folding:
       query = query.lower ()
    query = re.sub (r'[^ a-zA-Z0-9]', ' ', query)
    query = re.sub (r'\s+', ' ', query)
    query_words = query.split (' ')
    return query_words

def run_query(collection, query_words):
    # create accumulators and other data structures
    accum = {}
    filenames = []
    p = porter.PorterStemmer ()



    # get document lengths/titles
    titles = {}
    f = open (collection+"_index_len", "r")
    lengths = f.readlines ()
    f.close ()

    # get N
    N = len(lengths)

    # get index for each term and calculate similarities using accumulators
    for term in query_words:
        if term != '':
            if parameters.stemming:
                term = p.stem (term, 0, len(term)-1)
            if not os.path.isfile (collection+"_index/"+term):
               continue
            f = open (collection+"_index/"+term, "r")
            lines = f.readlines ()
            idf = 1
            if parameters.use_idf:
               df = len(lines)
               idf = 1/df
               if parameters.log_idf:
                  idf = math.log (1 + N/df)
            for line in lines:
                mo = re.match (r'([0-9]+)\:([0-9\.]+)', line)
                if mo:
                    file_id = mo.group(1)
                    tf = float (mo.group(2))
                    if not file_id in accum:
                        accum[file_id] = 0
                    if parameters.log_tf:
                        tf = (1 + math.log (tf))
                    accum[file_id] += (tf * idf)
            f.close()

    # parse lengths data and divide by |N| and get titles
    for l in lengths:
       mo = re.match (r'([0-9]+)\:([0-9\.]+)\:(.+)', l)
       if mo:
          document_id = mo.group (1)
          length = eval (mo.group (2))
          title = mo.group (3)
          if document_id in accum:
             if parameters.normalization:
                accum[document_id] = accum[document_id] / length
             titles[document_id] = title

    return accum, titles

# 2)Select top 20-30 (indicative number) terms from these documents using for instance tf-idf weights.
# To get these terms I could either go through each term in every document or i could through every term's index file
# I chose the latter else i'd be duplicating code of index.py (and to avoid regexes)

def BRF(collection, docIDs, query):
    idfs = {} # Document frequencies for the BRF most popular terms
    itfs = {} # Term frequencies for the BRF most popular terms
    term_accum = {}  # Overall ranking of each term

    query_words = clean_query(query)
    filenames = glob.glob(collection+ "_brf_index" + "/word_count.*") # Get list of filenames
    for f in filenames:
        docNo = f[f.find(".")+1:]
        if docNo in docIDs:
            contents = open(f, "r", encoding='utf-8')
            lines = contents.readlines()
            for line in lines: # Go through all the entries in the brf index file
                    mo = re.match (r'(.+)\:([0-9\.]+)', line)
                    if mo:
                        word = mo.group(1)
                        tf = mo.group(2)
                        if not word in itfs: # Increment the term frequency by the number of times is appears in the document
                            itfs[word] = tf
                        else:
                            itfs[word] += tf
                        if not word in idfs: # Increment the number of documents the term appears in by 1. Document frequency is local to the result set, not the entire document set
                            idfs[word] = 1
                        else:
                            idfs[word] += 1
            contents.close()

    # Calculate the overall "rank" of each term by tf / df
    for term in itfs:
        df = 1.0/idfs[term]
        tf = itfs[term]
        term_accum[term] = (float(tf) * float(df))
    # Don't think we can just naively do this the same way he does it for documents
    #   if parameters.log_idf:
    #        df = math.log (1 + N/idfs[term])
    #
    #    if parameters.log_tf:
    #        tf = (1 + math.log (tf))


    # Sort the term rankings
    result = sorted (term_accum, key=term_accum.__getitem__, reverse=True)

    # 3.1. Do Query Expansion, add these terms to query.
    # Expand the query - add the tK most popular words from the initial set

    i = 0
    while(i < parameters.BRF_tK):
        if result[i] not in query_words:
            query_words.append(result[i])
        i+=1

    # print("Expanded query words: " )
    # print(query_words)

    # 3.2. and then match the returned documents for this query and finally return the most relevant documents.
    # Copy and pasting his code from above for now, will sort into functions later

    # print top k results if BRF not enabled
    accum, titles = run_query(collection, query_words)
    return accum, titles

def main():
    # check parameter for collection name
    if len(sys.argv)<3:
       print ("Syntax: index.py <collection> <query>")
       exit(0)

    # construct collection and query
    collection = sys.argv[1]
    query = ''
    arg_index = 2
    while arg_index < len(sys.argv):
       query += sys.argv[arg_index] + ' '
       arg_index += 1

    # print("BRF Status: " + str(parameters.BRF))

    # print top k results if BRF not enabled
    accum,titles = run_query(collection, clean_query(query))
    result = sorted (accum, key=accum.__getitem__, reverse=True)

    if not parameters.BRF:
        for i in range (min (len (result), parameters.BRF_k)):
            print ("{0:10.8f} {1:5} {2}".format (accum[result[i]], result[i], titles[result[i]]))
        return

    docIDs = []
    for i in range (min (len (result), parameters.BRF_k)):
        docIDs.append(result[i]) # Store the doc ids of the top k documents
    accum, titles = BRF(collection, docIDs, query)
    result = sorted (accum, key=accum.__getitem__, reverse=True)

    if parameters.BRF:
        for i in range (min (len (result), parameters.BRF_k)):
            print ("{0:10.8f} {1:5} {2}".format (accum[result[i]], result[i], titles[result[i]]))

if __name__ == "__main__":
    main()
