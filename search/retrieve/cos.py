from queue import PriorityQueue
from search.indexengine.tokenizer import *
from search.indexengine.invertedindex import *
import json
import gzip
from math import inf, log, sqrt

from search.lib.funcs import load_lexicon, load_postings, open_json

class CosVector():
    def __init__(self, lexicon, cos_map, doc_id=None):
        self.n = lexicon['_tokens']
        self.N = lexicon['_N']
        self.w_top = {}
        self.doc_id = doc_id
        self._cos_map = cos_map

    def add_term(self, term_id, fik, nk):
        self.w_top[term_id] = (log(fik)+1)*log(self.N/nk)

    def add_term_q(self, term_id):
        self.w_top[term_id] = 1

    def __getitem__(self, key):
        if key in self.w_top:
            if self.doc_id == None:
                return self.w_top[key] 
            else:
                return self.w_top[key] / sqrt(self._cos_map[str(self.doc_id)])
        else:
            return 0

    def __mul__(self, other):
        if type(other) == type(self):
            s = 0
            for term in self.w_top:
                s += self[term] * other[term]
            return s
        else:
            raise ValueError(f'Invalid type for __mul__ "{type(other)}"')

class Cos():
    def __init__(self, indexs_dir):
        self.postings_file = indexs_dir + '/postings.bin'
        self.lexicon_file = indexs_dir + '/lexicon.json.gz'
        self._indexs_dir = indexs_dir
        self._postings: Postings = None
        self._cos_map = None

        self.lexicon = None
        
    def load_lexicon(self):
        """
        Loads lexicon file (path used is lexicon_file attribute)
        """
        self.lexicon = load_lexicon(self._indexs_dir)

    def set_postings(self, postings):
        self._postings = postings

    def load_postings(self):
        self._postings = load_postings(self._indexs_dir)
        self._cos_map = open_json(self._indexs_dir, 'cos_map.json.gz')

    def query_terms(self, terms):
        q = CosVector(self.lexicon, self._cos_map)
        dk = {}
        for term in terms:
            if term > 0: # if term in lexicon
                postings = self._postings.get_term(term)
                if len(postings) % 2 != 0:
                    print('incorrect len for ' + str(term) +
                        '  ' + str(len(postings)))
                ni = len(postings) / 2
                q.add_term_q(term)
                for i in range(0, len(postings), 2):
                    doc_id = postings[i]
                    fi = postings[i+1]
                    if not doc_id in dk:
                        dk[doc_id] = CosVector(self.lexicon, self._cos_map, doc_id=doc_id)
                    dk[doc_id].add_term(term, fi, ni)
        
        doc_scores = {}
        for doc_id in dk:
            doc = dk[doc_id]
            doc_scores[doc_id] = doc*q/sqrt(doc*doc)
        
        # get top 1000 docs
        q = PriorityQueue()
        max_score = -inf
        for key in doc_scores.keys():
            if q.qsize() < 1000:
                q.put((-doc_scores[key], key))
                if -doc_scores[key] > max_score:
                    max_score = -doc_scores[key]
            elif -doc_scores[key] < max_score:
                q.put((-doc_scores[key], key))
        docs = []
        for i in range(q.qsize() if q.qsize() < 1000 else 1000):
            item = q.get()
            docs.append([item[1], -item[0]])
        return docs

    def get_term_id(self, term):
        if term in self.lexicon:
            return self.lexicon[term]
        return -1

    def query(self, query: str):
        return self.query_terms(list(map(self.get_term_id, set(tokenize(query)))))
        