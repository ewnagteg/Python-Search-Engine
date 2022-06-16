from search.indexengine.tokenizer import *
from search.indexengine.invertedindex import *
import json
import gzip
from math import inf, log
from queue import PriorityQueue
from search.lib.funcs import semi_sort

class BM25():
    def __init__(self, indexs_dir):
        self.postings_file = indexs_dir + '/postings.bin'
        self.lexicon_file = indexs_dir + '/lexicon.json.gz'
        self._indexs_dir = indexs_dir
        self._postings: Postings = None
        self.lexicon = None
        
        self.k1 = 1.2
        self.k2 = 7
        self.b = 0.75

    def load_lexicon(self):
        """
        Loads lexicon file (path used is lexicon_file attribute)
        """
        with gzip.open(self.lexicon_file, 'rt') as file:
            self.lexicon = json.loads(file.read())

    def set_params(self, params):
        self.k1 = params[0]
        self.k2 = params[1]
        self.b = params[2]
    
    def set_postings(self, postings):
        self._postings = postings

    def load_postings(self):
        postings = Postings()
        postings.read(self.postings_file)
        self._postings = postings

    def query_terms(self, terms):
        doc_scores = {}
        query_count = {}
        for term in terms:
            if term in query_count:
                query_count[term] += 1
            else:
                query_count[term] = 1
        # calculate scores for docs
        avdl = self.lexicon['_avdl']
        N = self.lexicon['_N']
        for term in query_count:
            if term > 0: # if term in lexicon
                postings = self._postings.get_term(term)
                if len(postings) % 2 != 0:
                    print('incorrect len for ' + str(term) +
                        '  ' + str(len(postings)))
                ni = len(postings) / 2
                for i in range(0, len(postings), 2):
                    doc_id = postings[i]

                    dl = self.lexicon['_' + str(doc_id)]
                    K = self.k1 * ((1-self.b) + self.b*dl/avdl)
                    fi = postings[i+1]
                    qfi = query_count[term]
                    if not doc_id in doc_scores:
                        doc_scores[doc_id] = 0

                    doc_scores[doc_id] += (self.k1+1)*fi/(K+fi)*(self.k2+1)*qfi/(self.k2+qfi)*log((N-ni+0.5)/(ni+0.5)+1)

        q = PriorityQueue()
        max_score = -inf
        for key in doc_scores:
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
        return self.query_terms(list(map(self.get_term_id, tokenize(query))))

    def query_counts(self, query: str):
        terms = list(map(self.get_term_id, tokenize(query)))
        query_count = {}
        for term in terms:
            if term in query_count:
                query_count[term] += 1
            else:
                query_count[term] = 1
        return query_count
        