
import queue
from search.getdoc.getdoc import GetDoc
from search.retrieve.bm25 import BM25
from search.lib.timer import Timer
from time import time

from search.retrieve.snippets import Snippets

def main(index):
    query = 'some test'
    bm25 = BM25(index)

    # load data
    print('loading postings...')
    bm25.load_postings()
    print('loading lexicon...')
    bm25.load_lexicon()

    snips = Snippets(index)
    query_counts = bm25.query_counts(query)
    query = True
    while True:
        if query:
            i = input('Input search query:  ')
            s = time()
            result = bm25.query(i)
            snips.display_query(result[:10], i)
            e = time()
            print(f'Retrieval took {e-s} seconds')
            query = False
        if not query:
            n = input('Type rank of a document to view (N for new query, Q for quit): ')
        if n == 'Q':
            return
        if not n == 'N':
            rank = int(n) - 1
            docid = result[rank][0]
            print('\n\n')
            print(snips.get_doc(docid))
        else:
            query = True