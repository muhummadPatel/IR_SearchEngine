import copy
import math
import os
import sys

import parameters
import query as query_tool
from parameters import dprint


def get_queries(collection):
    collection_filenames = os.listdir(collection)
    query_filenames = [name for name in collection_filenames if "query" in name]
    dprint("query filenames:", query_filenames)

    queries = []
    for query_file in query_filenames:
        query_filepath = os.path.join(collection, query_file)
        with open(query_filepath, "r") as q:
            queries.append(q.read().splitlines()[0])
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
            int_rels = [int(i) for i in r.read().splitlines()]
            relevances.append(int_rels)
    dprint("relevances:", relevances)
    dprint("# relevance judgements for query 1:", len(relevances[0]))

    return relevances


def get_MAP(collection, queries, relevances, clip_res=False):
    query_count = 0
    avg_precision_sum = 0.0
    for query_idx, test_query in enumerate(queries):
        dprint("query for MAP:", test_query)
        similarity, result, titles = query_tool.get_result(collection, test_query, clip_results=clip_res)

        result_count = 0
        precision_avg_sum = 0.0
        precision_total = 0.0

        dprint("result", result)
        for i in range(len(result)):
            result_count += 1
            relevance_of_result = relevances[query_idx][int(result[i]) - 1] / 2.0
            precision_total += relevance_of_result
            precision_avg_sum += precision_total / result_count

            dprint("{0:10.8f} {1:5} {2}".format(similarity[result[i]], result[i], titles[result[i]]), end=" ")
            dprint(relevance_of_result)

        query_count += 1
        avg_precision_sum += precision_avg_sum / result_count
        dprint("avg precision_sum for query", precision_avg_sum / result_count)

    dprint("~> Mean Average Precision:", avg_precision_sum / query_count)
    return avg_precision_sum / query_count


# Pass in a single query and the set of relevance judgements for that query
# because NDCG is calculated for a single query (whereas MAP is calculated for
# a group of queries)
def get_NDCG(collection, test_query, query_relevances, clip_res=False):
    similarity, result, titles = query_tool.get_result(collection, test_query, clip_results=clip_res)

    actual_relevances = [query_relevances[int(r) - 1] for r in result]
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

def get_stats(collections, k, tk, clip_res=False):
    parameters.BRF_k = k
    parameters.BRF_tK = tk

    map_original_sum = map_BRF_only_sum = map_BRF_optimised_sum = map_overall_optimised_sum = 0.0
    ndcg_original_sum = ndcg_brf_only_sum = ndcg_brf_optimised_sum = ndcg_overall_optimised_sum = 0.0
    for collection in collections:
        queries = get_queries(collection)
        relevances = get_relevances(collection)

        parameters.original_as_received(collection)
        original = get_MAP(collection, queries, relevances, clip_res)

        ndcg_original_total = 0.0
        dprint("_____ NDCG for queries in", collection,"_____")
        for i in range(len(queries)):
            ndcg_original = get_NDCG(collection, queries[i], relevances[i], clip_res)

            ndcg_original_total += ndcg_original

            dprint("query:", queries[i].strip())
            dprint("NDCG original:", ndcg_original)

        ndcg_original_sum += (ndcg_original_total / len(queries))

        parameters.BRF_only()
        BRF_only = get_MAP(collection, queries, relevances, clip_res)

        ndcg_brf_only_total = 0.0
        dprint("_____ NDCG for queries in", collection,"_____")
        for i in range(len(queries)):
            ndcg_brf_only = get_NDCG(collection, queries[i], relevances[i], clip_res)

            ndcg_brf_only_total += ndcg_brf_only

            dprint("query:", queries[i].strip())
            dprint("NDCG brf_only:", ndcg_brf_only)

        ndcg_brf_only_sum += (ndcg_brf_only_total / len(queries))

        parameters.BRF_optimised(collection)
        BRF_optimised = get_MAP(collection, queries, relevances, clip_res)

        ndcg_brf_optimised_total = 0.0
        dprint("_____ NDCG for queries in", collection,"_____")
        for i in range(len(queries)):
            ndcg_brf_optimised = get_NDCG(collection, queries[i], relevances[i], clip_res)

            ndcg_brf_optimised_total += ndcg_brf_optimised

            dprint("query:", queries[i].strip())
            dprint("NDCG brf_optimised:", ndcg_brf_optimised)

        ndcg_brf_optimised_sum += (ndcg_brf_optimised_total / len(queries))

        parameters.overall_optimised()
        overall_optimised = get_MAP(collection, queries, relevances, clip_res)

        ndcg_overall_optimised_total = 0.0
        dprint("_____ NDCG for queries in", collection,"_____")
        for i in range(len(queries)):
            ndcg_overall_optimised = get_NDCG(collection, queries[i], relevances[i], clip_res)

            ndcg_overall_optimised_total += ndcg_overall_optimised

            dprint("query:", queries[i].strip())
            dprint("NDCG overall optimised:", ndcg_overall_optimised)

        ndcg_overall_optimised_total += (ndcg_overall_optimised_total / len(queries))

        map_original_sum += original
        map_BRF_only_sum += BRF_only
        map_BRF_optimised_sum += BRF_optimised
        map_overall_optimised_sum += overall_optimised

        dprint("_____ Mean average precision for", collection,"_____")
        dprint("MAP original:", original)
        dprint("MAP BRF only:", BRF_only, "\n")
        dprint("MAP BRF optimised:", BRF_optimised)
        dprint("MAP global optimised:", overall_optimised, "\n")


    num_testbeds = len(collections)
    avg_map_original = map_original_sum / num_testbeds
    avg_map_brf_only = map_BRF_only_sum / num_testbeds
    avg_map_brf_optimised = map_BRF_optimised_sum / num_testbeds
    avg_map_overall_optimised = map_BRF_optimised_sum / num_testbeds

    avg_ndcg_original = ndcg_original_sum / num_testbeds
    avg_ndcg_brf_only = ndcg_brf_only_sum / num_testbeds
    avg_ndcg_brf_optimised = ndcg_brf_optimised_sum / num_testbeds
    avg_ndcg_overall_optimised = ndcg_overall_optimised_sum / num_testbeds

    return {
        "num_testbeds": num_testbeds,
        "avg_map_original": avg_map_original,
        "avg_map_brf_only": avg_map_brf_only,
        "avg_map_brf_optimised": avg_map_brf_optimised,
        "avg_map_overall_optimised": avg_map_overall_optimised,
        "avg_ndcg_original": avg_ndcg_original,
        "avg_ndcg_brf_only": avg_ndcg_brf_only,
        "avg_ndcg_brf_optimised": avg_ndcg_brf_optimised,
        "avg_ndcg_overall_optimised": avg_ndcg_overall_optimised
    }


def explore_params(collections):
    stats10 = {}
    stats200 = {}
    highest_k = -1
    highest_tk = -1
    highest_map = -1
    for k in range(1, 21):
        print("k", k)
        for tk in range(3, 26):
            stats10_temp = get_stats(collections, k, tk, clip_res=True)
            stats200_temp = get_stats(collections, k, tk, clip_res=False)

            if stats10_temp["avg_map_after"] > highest_map:
                highest_k = k
                highest_tk = tk
                highest_map = stats10_temp["avg_map_after"]

                stats10 = copy.deepcopy(stats10_temp)
                stats200 = copy.deepcopy(stats200_temp)

    print("Best params identified:")
    print("highest k =", highest_k, ", highest tk=", highest_tk)

    return stats10, stats200


def main(collections):
    stats10 = {}
    stats200 = {}

    if parameters.BRF_explore_params:
        stats10, stats200 = explore_params(collections)
    else:
        k = parameters.BRF_k
        tk = parameters.BRF_tK
        stats10 = get_stats(collections, k, tk, clip_res=True)
        stats200 = get_stats(collections, k, tk, clip_res=False)

    print("\n_____ Summary _____")
    print("Testbeds run:", stats10["num_testbeds"])
    print("=====")
    print("Using 10 results:")
    print("-----")
    print("avg_map_original:", stats10["avg_map_before"])
    print("avg_map_brf_only:", stats10["avg_map_after"])
    print("avg_map_brf_optimised:", stats10["avg_map_before"])
    print("avg_map_overall_optimised:", stats10["avg_map_after"])
    print("-----")
    print("avg_ndcg_original:", stats10["avg_ndcg_before"])
    print("avg_ndcg_brf_only:", stats10["avg_ndcg_after"])
    print("avg_ndcg_brf_optimised:", stats10["avg_ndcg_before"])
    print("avg_ndcg_overall_optimised:", stats10["avg_ndcg_after"])
    print("=====")
    print("Using 200 results:")
    print("-----")
    print("avg_map_original:", stats200["avg_map_before"])
    print("avg_map_brf_only:", stats200["avg_map_after"])
    print("avg_map_brf_optimised:", stats200["avg_map_before"])
    print("avg_map_overall_optimised:", stats200["avg_map_after"])
    print("-----")
    print("avg_ndcg_original:", stats200["avg_ndcg_before"])
    print("avg_ndcg_brf_only:", stats200["avg_ndcg_after"])
    print("avg_ndcg_brf_optimised:", stats200["avg_ndcg_before"])
    print("avg_ndcg_overall_optimised:", stats200["avg_ndcg_after"])
    print("=====")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Syntax: report.py <collection>|<all>")
        exit(0)

    if sys.argv[1] == "all":
        #TODO: find a valid copy of testbed 10
        collections = ["testbed" + str(i) for i in range(1, 17) if i != 10]
    else:
        collections = [sys.argv[1]]

    main(collections)
