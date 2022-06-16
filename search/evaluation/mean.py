from search.parsers.qrels import Qrels
from search.parsers.results import Results


def average_precision(qrel: Qrels, results: Results, queryid: str, limit=0):
    rel_doc_cnt = 0
    total = 0
    for i, result in enumerate(results.get_result(queryid)):
        relevant = qrel.get_relevance(queryid, result.doc_id)
        if relevant == None:
            print(f'{queryid}, {result.doc_id}')
        relevant = 1 if relevant > 0 else 0
        rel_doc_cnt += relevant
        total += relevant * rel_doc_cnt / (i + 1) * 1.0 if i < 1000 else 0
        if (i + 1) >= limit and (limit != 0 or i >= 1000):
            break
    return total / qrel.get_num_rel_docs(queryid) if limit == 0 else rel_doc_cnt / limit

def mean_average_precision(qrel: Qrels, result: Results, limit=0):
    total = 0
    for queryid in qrel.get_query_ids():
        # stops it from breaking when missing query (like msmucker's)
        if result.get_result(queryid) != None:
            total += average_precision(qrel, result, queryid, limit=limit)
    return total / len(qrel.get_query_ids())

