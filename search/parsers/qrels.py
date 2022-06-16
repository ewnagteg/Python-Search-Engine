# Author: Eric Nagtegaal modified code by Nimesh Ghelani based on code by Mark D. Smucker
from collections import defaultdict
class Judgement():
    def __init__(self, query_id, doc_id, relevance):
        self.query_id = query_id
        self.doc_id = doc_id
        self.relevance = relevance

    def key(self):
        return self.query_id + '-' + self.doc_id
    
class Qrels():
    def __init__(self):
        self.judgments = {}
        self.query_to_reldocnos = defaultdict(set)

    def add_judgement(self, judgement):
        if judgement.key() in self.judgments:
            raise Exception('Cannot have duplicate queryID and docID data points')
        self.judgments[judgement.key()] = judgement
        if judgement.relevance != 0:
            self.query_to_reldocnos[judgement.query_id].add(judgement.doc_id)
    
    def get_query_ids(self):
        return self.query_to_reldocnos.keys()

    def get_relevance(self, query_id, docid):
        key = f'{query_id}-{docid}'
        if key in self.judgments:
            return self.judgments[key].relevance
        return 0

    def get_num_rel_docs(self, queryid):
        return len(self.query_to_reldocnos[queryid])

def parse_qrels(file):
    qrels = Qrels()
    with open(file) as data:
        for row_txt in data:
            row = row_txt.strip().split()
            if len(row) != 4:
                raise ValueError(f'Invalid format for line "{row_txt}"')
            qid, _, doc_id, relevance = row
            relevance = int(relevance)
            qrels.add_judgement(Judgement(qid, doc_id, relevance))
    return qrels


