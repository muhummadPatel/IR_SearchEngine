import os
import sys

import query as query_tool
import parameters

def get_queries(collection):
    collection_filenames = os.listdir(collection)
    query_filenames = [name for name in collection_filenames if "query" in name]
    # print(query_filenames)

    queries = []
    for query_file in query_filenames:
        query_filepath = os.path.join(collection, query_file)
        with open(query_filepath, "r") as q:
            queries.append(q.readlines()[0])
    # print(queries)

    return queries


def get_relevances(collection):
    collection_filenames = os.listdir(collection)
    relevance_filenames = [name for name in collection_filenames if "relevance" in name]
    # print(relevance_filenames)

    relevances = []
    for rel_file in relevance_filenames:
        rel_filepath = os.path.join(collection, rel_file)
        with open(rel_filepath, "r") as r:
            int_rels = [int(i) for i in r.readlines()]
            relevances.append(int_rels)
    # print(relevances)
    # print(len(relevances[0]))

    return relevances


def get_MAP(collection, queries, relevances):
    query_count = 0
    avg_precision_sum = 0.0
    for query_idx, test_query in enumerate(queries):
        # print("query:", test_query)
        similarity, result, titles = query_tool.get_result(collection, test_query)

        result_count = 0
        precision_sum = 0.0
        for i in range(len(result)):
            result_count += 1
            relevance_of_result = relevances[query_idx][int(result[i])-1] / 2.0
            precision_sum += relevance_of_result / result_count

            # print("{0:10.8f} {1:5} {2}".format(similarity[result[i]], result[i], titles[result[i]]), end=" ")
            # print(relevance_of_result)
        # print()

        query_count += 1
        avg_precision_sum += precision_sum / query_count

    # print("~> Mean Average Precision:", avg_precision_sum / query_count)
    return avg_precision_sum / query_count


def main(collection):
    queries = get_queries(collection)
    relevances = get_relevances(collection)

    parameters.BRF = False
    map_before = get_MAP(collection, queries, relevances)
    parameters.BRF = True
    map_after = get_MAP(collection, queries, relevances)
    print("MAP before BRF:", map_before)
    print("MAP after BRF:", map_after)

if __name__ == "__main__":
    if len(sys.argv) < 2:
       print ("Syntax: report.py <collection>")
       exit(0)

    main(sys.argv[1])
