debug_print = False
BRF_explore_params = True
normalization = True
stemming = False
case_folding = True
stop_words = True
log_tf = True
use_idf = True
log_idf = True
BRF = True
BRF_k = 3
BRF_tK = 3


# Set parameters for each test scenario
def original_as_received():
    global normalization
    global stemming
    global case_folding
    global stop_words
    global log_tf
    global use_idf
    global log_idf
    global BRF
    global BRF_k
    global BRF_tK

    normalization = True
    stemming = True
    case_folding = True
    stop_words = True
    log_tf = True
    use_idf = True
    log_idf = True
    BRF = False
    BRF_k = -1
    BRF_tK = -1


def BRF_only():
    global normalization
    global stemming
    global case_folding
    global stop_words
    global log_tf
    global use_idf
    global log_idf
    global BRF
    global BRF_k
    global BRF_tK

    normalization = True
    stemming = True
    case_folding = True
    stop_words = True
    log_tf = True
    use_idf = True
    log_idf = True
    BRF = True
    if not BRF_explore_params:
        BRF_k = 1
        BRF_tK = 3


def BRF_optimised():
    global normalization
    global stemming
    global case_folding
    global stop_words
    global log_tf
    global use_idf
    global log_idf
    global BRF
    global BRF_k
    global BRF_tK

    normalization = True
    stemming = False
    case_folding = True
    stop_words = True
    log_tf = False
    use_idf = True
    log_idf = False
    BRF = True
    if not BRF_explore_params:
        BRF_k = 1
        BRF_tK = 1


def overall_optimised():
    global normalization
    global stemming
    global case_folding
    global stop_words
    global log_tf
    global use_idf
    global log_idf
    global BRF
    global BRF_k
    global BRF_tK

    normalization = True
    stemming = False
    case_folding = True
    stop_words = True
    log_tf = False
    use_idf = True
    log_idf = False
    BRF = True
    BRF_k = 1
    BRF_tK = 1


# Utility functions
def dprint(*args, end="\n"):
    if debug_print:
        print(args, end)
