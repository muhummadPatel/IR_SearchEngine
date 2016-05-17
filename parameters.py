# simple extended boolean search engine: configurable parameters
# Hussein Suleman
# 21 April 2016

debug_print = False
normalization = True
stemming = False
case_folding = True
stop_words = True
log_tf = False
use_idf = True
log_idf = False
BRF = True
BRF_k = 6
BRF_tK = 9
BRF_explore_params = True


# Utility functions
def dprint(*args, end="\n"):
    if debug_print:
        print(args, end)
