# Simple extended boolean search engine: query module
# Hussein Suleman
# 14 April 2016

import glob
import math
import os
import re
import sys

import parameters
import porter
from parameters import dprint


def clean_query(query, stop_words):
    # clean query
    if parameters.case_folding:
        query = query.lower()
    query = re.sub(r'[^ a-zA-Z0-9]', ' ', query)
    query = re.sub(r'\s+', ' ', query)
    query_words = query.split(' ')

    p = porter.PorterStemmer()
    if parameters.stop_words:
        query_words = [query_word for query_word in query_words if query_word not in stop_words]
    if parameters.stemming:
        query_words = [p.stem(query_word, 0, len(query_word) - 1) for query_word in query_words]

    return query_words


def run_query(collection, query_words):
    # create accumulators and other data structures
    accum = {}
    p = porter.PorterStemmer()

    # get document lengths/titles
    titles = {}
    f = open(collection + "_index_len", "r")
    lengths = f.read().splitlines()
    f.close()

    # get N
    n = len(lengths)

    # get index for each term and calculate similarities using accumulators
    for term in query_words:
        if term != '':
            f = None
            if parameters.stemming:
                term = p.stem(term, 0, len(term) - 1)
                if not os.path.isfile(collection + "_stemmed_index/_" + term):
                    continue
                f = open(collection + "_stemmed_index/_" + term, "r")
            else:
                if not os.path.isfile(collection + "_index/_" + term):
                    continue
                f = open(collection + "_index/_" + term, "r")
            lines = f.read().splitlines()
            idf = 1
            if parameters.use_idf:
                df = len(lines)
                idf = 1 / df
                if parameters.log_idf:
                    idf = math.log(1 + n / df)
            for line in lines:
                mo = re.match(r'([0-9]+):([0-9\.]+)', line)
                if mo:
                    file_id = mo.group(1)
                    tf = float(mo.group(2))
                    if file_id not in accum:
                        accum[file_id] = 0
                    if parameters.log_tf:
                        tf = (1 + math.log(tf))
                    accum[file_id] += (tf * idf)
            f.close()

    # parse lengths data and divide by |N| and get titles
    for l in lengths:
        mo = re.match(r'([0-9]+):([0-9\.]+):(.+)', l)
        if mo:
            document_id = mo.group(1)
            length = eval(mo.group(2))
            title = mo.group(3)
            if document_id in accum:
                if parameters.normalization:
                    accum[document_id] = accum[document_id] / length
                titles[document_id] = title

    return accum, titles


# 2)Select top 20-30 (indicative number) terms from these documents using for instance tf-idf weights.
# To get these terms I could either go through each term in every document or i could through every term's index file
# I chose the latter else i'd be duplicating code of index.py (and to avoid regexes)

def BRF(collection, doc_ids, query, stop_words):
    idfs = {}  # Document frequencies for the BRF most popular terms
    itfs = {}  # Term frequencies for the BRF most popular terms
    term_accum = {}  # Overall ranking of each term

    query_words = clean_query(query, stop_words)
    filenames = None
    if parameters.stemming:
        filenames = glob.glob(collection + "_stemmed_brf_index" + "/word_count.*")  # Get list of filenames
    else:
        filenames = glob.glob(collection + "_brf_index" + "/word_count.*")  # Get list of filenames
    for f in filenames:
        doc_no = f[f.find(".") + 1:]
        if doc_no in doc_ids:
            contents = open(f, "r", encoding='utf-8')
            lines = contents.read().splitlines()
            for line in lines:  # Go through all the entries in the brf index file
                mo = re.match(r'(.+):([0-9\.]+)', line)
                if mo:
                    word = mo.group(1)
                    tf = mo.group(2)
                    # Increment the term frequency by the number of times is appears in the document
                    if word not in itfs:
                        itfs[word] = tf
                    else:
                        itfs[word] += tf
                    # Increment the number of documents the term appears in by 1. Document frequency is local to the result set, not the entire document set
                    if word not in idfs:
                        idfs[word] = 1
                    else:
                        idfs[word] += 1
            contents.close()

    # Calculate the overall "rank" of each term by tf / df
    for term in itfs:
        df = 1.0 / idfs[term]
        tf = itfs[term]
        term_accum[term] = (float(tf) * float(df))
    # Don't think we can just naively do this the same way he does it for documents
    #   if parameters.log_idf:
    #        df = math.log (1 + N/idfs[term])
    #
    #    if parameters.log_tf:
    #        tf = (1 + math.log (tf))

    # Sort the term rankings
    result = sorted(term_accum, key=term_accum.__getitem__, reverse=True)

    # 3.1. Do Query Expansion, add these terms to query.
    # Expand the query - add the tK most popular words from the initial set

    i = 0
    g = 0
    p = porter.PorterStemmer()
    while i < parameters.BRF_tK and g < len(result):
        if result[g] not in stop_words and result[g] not in query_words:
            if parameters.stemming:
                query_words.append(p.stem(result[g], 0, len(result[g]) - 1))
            else:
                query_words.append(result[g])
            i += 1
        g += 1


    dprint("Expanded query words: ")
    dprint(query_words)

    # 3.2. and then match the returned documents for this query and finally return the most relevant documents.
    # Copy and pasting his code from above for now, will sort into functions later

    # print top k results if BRF not enabled
    accum, titles = run_query(collection, query_words)
    return accum, titles


# set clip_results to False to return the full list of docs with associated vars
def get_result(collection, query, clip_results=True):
    # Stop words is an empty set unless parameter is set
    stop_words = set()
    if parameters.stop_words:
        stop_words_file = open("stop-word-list.txt", "r")
        stop_words = set(stop_words_file.read().splitlines())

    # print top k results if BRF not enabled
    accum, titles = run_query(collection, clean_query(query, stop_words))
    result = sorted (accum, key=accum.__getitem__, reverse=True)

    if not parameters.BRF:
        final_result = result[0:min (len (result), 10)] if clip_results else result
        return accum, final_result, titles

    doc_ids = []
    for i in range(min(len(result), parameters.BRF_k)):
        doc_ids.append(result[i])  # Store the doc ids of the top k documents

    accum, titles = BRF(collection, doc_ids, query, stop_words)
    result = sorted(accum, key=accum.__getitem__, reverse=True)

    if parameters.BRF:
        final_result = result[0:min (len (result), 10)] if clip_results else result
        return accum, final_result, titles

def main():
    # check parameter for collection name
    if len(sys.argv) < 3:
        print("Syntax: index.py <collection> <query>")
        exit(0)

    # construct collection and query
    collection = sys.argv[1]
    query = ''
    arg_index = 2
    while arg_index < len(sys.argv):
        query += sys.argv[arg_index] + ' '
        arg_index += 1

    print("BRF Status: " + str(parameters.BRF))
    accum, final_result, titles = get_result(collection, query)

    for i in range(len(final_result)):
        print("{0:10.8f} {1:5} {2}".format(accum[final_result[i]], final_result[i], titles[final_result[i]]))


if __name__ == "__main__":
    main()
