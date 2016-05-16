# simple extended boolean search engine: configurable parameters
# Hussein Suleman
# 21 April 2016

debug_print = False
normalization = True
stemming = True
case_folding = True
stop_words = True
log_tf = True
use_idf = True
log_idf = True
BRF = True
BRF_k = 1
BRF_tK = 3
BRF_explore_params = False


# Utility functions
def dprint(*args, end="\n"):
    if debug_print:
        print(args, end)
