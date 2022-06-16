from search.parsers.qrels import Qrels
from search.parsers.results import Results
from math import e, log

h = 224
Dt = lambda t: e**(-t*log(2)/h)
T_D = lambda l: 0.018 * l + 7.8
T_S = 4.4
P = lambda r: 0.64 if r==1 else 0.39
gk = 1 * 0.64 * 0.77
Tx = T_S + T_D(0) * 0.64
N = 1

def tbg(qrel: Qrels, results: Results, queryid: str, token_counts):
    total = 0
    sum_Tk = 0
    for result in results.get_result(queryid):
        relevant = 1 if qrel.get_relevance(queryid, result.doc_id) > 0 else 0
        total += Dt(sum_Tk) * relevant * gk
        sum_Tk += T_S + T_D(token_counts[result.doc_id]) * P(relevant)
    return total / N

def mean_tbg(qrel: Qrels, result: Results, token_counts):
    total = 0
    cnt = 0
    for queryid in qrel.get_query_ids():
        # stops it from breaking when missing query (like msmucker's)
        if result.get_result(queryid) != None:
            total += tbg(qrel, result, queryid, token_counts)
            cnt += 1
    return total / cnt