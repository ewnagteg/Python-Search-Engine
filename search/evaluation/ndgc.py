from search.parsers.qrels import Qrels
from search.parsers.results import Results
from math import log2

def idcg(qrel: Qrels, queryid: str, limit: int):
    n = qrel.get_num_rel_docs(queryid)
    n = n if n < limit else limit
    total = 0
    for i in range(1, n+1):
        total += 1 / log2(i + 1)
    return total if total > 0 else 1

def ndcg(qrel: Qrels, results: Results, queryid: str, limit: int):
    total = 0
    for i, result in enumerate(results.get_result(queryid)):
        relevant = qrel.get_relevance(queryid, result.doc_id)
        relevant = 1 if relevant > 0 else 0
        total += relevant / log2(i + 2)
        if (i + 1) >= limit:
            break
    return total / idcg(qrel, queryid, limit)

def mean_ndcg(qrel: Qrels, result: Results, limit: int):
    total = 0
    for queryid in qrel.get_query_ids():
        # stops it from breaking when missing query (like msmucker's)
        if result.get_result(queryid) != None:
            total += ndcg(qrel, result, queryid, limit)
    return total / len(qrel.get_query_ids())