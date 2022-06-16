import enum
from search.indexengine.tokenizer import *
from search.indexengine.invertedindex import *
import json
import gzip

class BooleanAnd():
    """
    BoolanAND search class

    Can do boolean search, ranks and score determined by order in postings array

    Attributes
    ----------
    postings_file : str
        Path to postings file
    lexicon_file : str
        Path to lexicon file
    _index_dir : str
        Path to dir containing indexes (output dir of index engine)
    _postings : search.tokenizer.tokenizer.Postings
    
    """
    def __init__(self, indexs_dir):
        self.postings_file = indexs_dir + '/postings.bin'
        self.lexicon_file = indexs_dir + '/lexicon.json.gz'
        self._indexs_dir = indexs_dir
        self._postings: Postings = None
        self.lexicon = None
        
    def load_lexicon(self):
        """
        Loads lexicon file (path used is lexicon_file attribute)
        """
        with gzip.open(self.lexicon_file, 'rt') as file:
            self.lexicon = json.loads(file.read())

    def set_postings(self, postings):
        self._postings = postings

    def load_postings(self):
        postings = Postings()
        postings.read(self.postings_file)
        self._postings = postings

    def query_terms(self, terms):
        doc_count = {}
        for term in terms:
            if term > 0: # if term in lexicon
                postings = self._postings.get_term(term)
                if len(postings) % 2 != 0:
                    print('incorrect len for ' + str(term) +
                        '  ' + str(len(postings)))
                for i in range(0, len(postings), 2):
                    doc_id = postings[i]


                    if doc_id in doc_count:
                        doc_count[doc_id] += 1
                    else:
                        doc_count[doc_id] = 1
        docs = list(
            filter(lambda x: doc_count[x] == len(terms), doc_count.keys()))
        docs_list = [[key, i] for i, key in enumerate(docs)]
        return docs_list

    def get_term_id(self, term):
        if term in self.lexicon:
            return self.lexicon[term]
        return -1

    def query(self, query: str):
        """
        Runs boolean and retrieval on with given query string
        """
        return self.query_terms(list(map(self.get_term_id, set(tokenize(query)))))
