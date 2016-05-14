import math
import os
import sys

import query as query_tool
import parameters

# set verbose=True to enable debug printlines
verbose = False


def dprint(*args, end="\n"):
    global verbose
    if verbose:
        print(args, end)

def get_queries(collection):
    collection_filenames = os.listdir(collection)
    query_filenames = [name for name in collection_filenames if "query" in name]
    dprint("query filenames:", query_filenames)

    queries = []
    for query_file in query_filenames:
        query_filepath = os.path.join(collection, query_file)
        with open(query_filepath, "r") as q:
            queries.append(q.readlines()[0])
    dprint("queries:", queries)

    return queries


def get_relevances(collection):
    collection_filenames = os.listdir(collection)
    relevance_filenames = [name for name in collection_filenames if "relevance" in name]
    dprint("relevance filenames:", relevance_filenames)

    relevances = []
    for rel_file in relevance_filenames:
        rel_filepath = os.path.join(collection, rel_file)
        with open(rel_filepath, "r") as r:
            int_rels = [int(i) for i in r.readlines()]
            relevances.append(int_rels)
    dprint("relevances:", relevances)
    dprint("# relevance judgements for query 1:", len(relevances[0]))

    return relevances


def get_MAP(collection, queries, relevances):
    query_count = 0
    avg_precision_sum = 0.0
    for query_idx, test_query in enumerate(queries):
        dprint("query for MAP:", test_query)
        similarity, result, titles = query_tool.get_result(collection, test_query)

        result_count = 0
        precision_sum = 0.0
        for i in range(len(result)):
            result_count += 1
            relevance_of_result = relevances[query_idx][int(result[i])-1] / 2.0
            precision_sum += relevance_of_result / result_count

            dprint("{0:10.8f} {1:5} {2}".format(similarity[result[i]], result[i], titles[result[i]]), end=" ")
            dprint(relevance_of_result)
        dprint()

        query_count += 1
        avg_precision_sum += precision_sum / query_count

    dprint("~> Mean Average Precision:", avg_precision_sum / query_count)
    return avg_precision_sum / query_count


# Pass in a single query and the set of relevance judgements for that query
# because NDCG is calculated for a single query (whereas MAP is calculated for
# a group of queries)
def get_NDCG(collection, test_query, query_relevances):
    similarity, result, titles = query_tool.get_result(collection, test_query)

    actual_relevances = [query_relevances[int(r)-1] for r in result]
    ideal_relevances = sorted(actual_relevances, reverse=True)
    dprint("actual_relevances:", actual_relevances)
    dprint("ideal_relevances:", ideal_relevances)

    disc_cum_gain = 0
    ideal_disc_cum_gain = 0
    for i in range(len(result)):

        # need to use i+2 because i starts at 0, not 1
        disc_cum_gain += (actual_relevances[i] / math.log(i + 2, 2))
        ideal_disc_cum_gain += (ideal_relevances[i] / math.log(i + 2, 2))

    try:
        norm_disc_cum_gain = disc_cum_gain / ideal_disc_cum_gain
        return norm_disc_cum_gain
    except ZeroDivisionError:
        # TODO: Figure out how to handle this properly
        dprint("ZeroDivError", disc_cum_gain, ideal_disc_cum_gain)
        dprint("actual_relevances:", actual_relevances)
        dprint("ideal_relevances:", ideal_relevances)
        return -1

def main(collection):
    queries = get_queries(collection)
    relevances = get_relevances(collection)

    parameters.BRF = False
    map_before = get_MAP(collection, queries, relevances)
    parameters.BRF = True
    map_after = get_MAP(collection, queries, relevances)

    print("_____ Mean average precision for", collection,"_____")
    print("MAP before BRF:", map_before)
    print("MAP after BRF:", map_after, "\n")

    # Have to use a loop for NDCG calculations because NDCG is done per query
    # not per set of queries like MAP
    print("_____ NDCG for queries in", collection,"_____")
    for i in range(len(queries)):
        parameters.BRF=False
        ndcg_before = get_NDCG(collection, queries[i], relevances[i])
        parameters.BRF=True
        ndcg_after = get_NDCG(collection, queries[i], relevances[i])

        print("query:", queries[i].strip())
        print("NDCG before BRF:", ndcg_before)
        print("NDCG after BRF:", ndcg_after, "\n")



if __name__ == "__main__":
    if len(sys.argv) < 2:
       print ("Syntax: report.py <collection>")
       exit(0)

    main(sys.argv[1])
