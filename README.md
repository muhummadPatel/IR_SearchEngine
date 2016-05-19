##CS Honours 2016: Information Retrieval - *Assignment 1b*

###Group Members:
* Aashiq Parker *(prkaas003)*
* Brian Mc George *(mcgbri004)*
* Muhummad Patel *(ptlmuh006)*

###Description:
This assignment required us to modify a sample search engine to include Blind Relevance Feedback (BRF)
along with any other performance enhancing optimistions. The sample search engine provided was written
as a collection of scripts that had to be refactored to allow us to neatly add on our improvements. We
were also provided with a suite of 16 testbeds with which to measure the effectiveness of our search
engine. The following is a list of the important scripts in our final implementation, their purpose,
and usage datails (where appropriate):

* **index.py**
  * Creates the neccessary indexes for a particular testbed
  * *Usage:* `python3 index.py <testbedN>` - where <testbedN> in the testbed you wish to index
* **indexing_util.py**
  * Cleans up old indexes and creates new indexes in bulk. This is useful if you want to index/re-index
    the entire suite of testbeds.
  * *Usage:* `python3 indexing_util.py` - this will remove any existing indexes and index all testbeds.
* **parameters.py**
  * This controls the various features of the search engine. Features like stemming and stopwords can be
    toggled by setting the appropriate varibales in this script to either True, or False.
  * This script also contains functions used to keep track of the 3 sets of paramter values that we used 
    for testing, namely: Original/baseline search engine, search engine with only BRF, search engine with 
    BRF and additional optimisations.
* **query.py**
  * Runs a query on a specific testbed/collection. This is also where the BRF feature was implemented.
  * *Usage:* `python3 query.py <testbedN> <query to run>`
* **report.py**
  * Runs the testbed(s) and outputs the Mean Average Precision (MAP) and Normalised Discounted Cumulative Gain
    (NDCG) for that testbed. It will run the testbed(s) using the query and relevances file contained in the
    testbed folder. This is the script that was used to generate the final results for this assignment.
  * Can run either over a single testbed, or over all testbeds.
  * *Usage:* `python3 report.py <test case>` - where <test case> is either a single testbed (e.g. testbed14),
    or 'all' (to run over all testbeds).

