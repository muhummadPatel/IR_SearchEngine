import os
import sys

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


def main(collection):
    queries = get_queries(collection)
    relevances = get_relevances(collection)


if __name__ == "__main__":
    main(sys.argv[1])
