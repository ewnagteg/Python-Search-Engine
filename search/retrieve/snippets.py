from queue import PriorityQueue
from search.getdoc.getdoc import GetDoc
from search.indexengine.tokenizer import remove_tags, tokenize
import re
from search.lib.funcs import load_lexicon, query_counts

class Snippets():
    def __init__(self, index, lexicon=None) -> None:
        self._index = index
        self._getdoc = GetDoc(index)
        self._lexicon = lexicon
        self._c_w = 1
        self._d_w = 1
        self._k_w = 1
        self._l_w = 1
        if lexicon == None:
            self._lexicon = load_lexicon(index)

    def _limit_sentence(self, sentence):
        return sentence if len(sentence) < 256 else sentence[:256] + '... '
        
    def get_snippet(self, doc_txt, query, n=5):
        sentences = filter(lambda x: len(x) > 5, re.split('(?<=[.!?])', remove_tags(doc_txt)))
        # need qcounts
        # do smuckers alg
        ranks = PriorityQueue()
        qcounts = query_counts(query, self._lexicon)
        l = 2
        for sentence in sentences:
            # ignore h because of #86 on campuswire
            get_term_id = lambda term : self._lexicon if term in self._lexicon else -1
            tokens = map(get_term_id, tokenize(sentence))
            c = sum([1 if token in qcounts else 0 for token in tokens])
            d = sum([1 if token in tokens else 0 for token in qcounts])
            k = 0
            kcur = 0
            for token in tokens:
                if token in qcounts:
                    kcur += 1
                else:
                    if kcur > k:
                        k = kcur
                    kcur = 0
            l -= 1 if l > 0 else 0
            ranks.put([-(self._c_w*c+self._d_w*d+self._k_w*k+self._l_w*l), sentence])
        return ''.join([self._limit_sentence(ranks.get()[1]) for i in range(n)])

    def display_query(self, query_result, query):
        print()
        for rank, result in enumerate(query_result):
            doc_id, score = result
            doc = self._getdoc.get_doc_id(doc_id)
            headline = doc['headline']
            date = doc['date']
            docno = 'LA' + doc['docno']
            txt = doc['text']
            txt = re.sub(' +', ' ', txt)
            txt = re.sub('\n+', '', txt)
            snippet = self.get_snippet(txt, query)
            if len(headline) == 0:
                headline = snippet[:50]
                headline += '...' if len(snippet) > 50 else ''
            print(f'{rank+1}. {headline} ({date})')
            print(f'{snippet} ({docno})')
            print('\n')

    def get_doc(self, docid):
        return self._getdoc.get_doc_id(docid)['file']