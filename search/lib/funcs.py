import datetime
from math import inf
import os
import gzip
import json

from search.indexengine.invertedindex import Postings
from search.indexengine.tokenizer import tokenize

def convert_date(date: str):
    nums = list(map(int, date.split('/')))
    nums[0] += 1900
    return convert_date(*nums)

def convert_date(yy, mm, dd):
    # %-d does not work on windows hence this
    formatstring = '%B %#d, %Y' if os.name == 'nt' else '%B %-d, %Y'
    date = datetime.datetime(int(yy), int(mm), int(dd))
    return date.strftime(formatstring)

def open_json(index_dir, fname):
    l = ''
    with gzip.open(index_dir + '/' + fname, 'rt') as file:
        l = json.loads(file.read())
    return l

def load_lexicon(index_dir):
    return open_json(index_dir, 'lexicon.json.gz')

def load_uid_map(index_dir):
    return open_json(index_dir, 'uid_map.json.gz')

def save_json(data, fname, index_dir):
    with open(index_dir + '/' + fname, 'wb') as out:
        out.write(
            gzip.compress(bytes(json.dumps(data), 'utf-8'))
        )

def load_postings(index_dir):
    postings = Postings()
    postings.read(index_dir + '/postings.bin')
    return postings

def semi_sort(docs_scores):
    buckets = {}
    for k in range(10):
        buckets[k] = []
    for i in docs_scores:
        score = docs_scores[i]
        if score > 99:
            buckets[9].append(i)
        else:
            digit = int((score%100)/10)
            buckets[digit].append(i)
    arr = []
    for i in range(10):
        arr.extend(buckets[9-i])
    return arr

def query_counts(query, lexicon):
    """
    Returns dict containing term counts for query.
    """
    get_term_id = lambda term : lexicon[term] if term in lexicon else -1
    return list(map(get_term_id, tokenize(query)))

class TokenCounts():
    """
    Easiest way of getting token lengths efficiently is just using what's in lexicon
    Hence why this exists.
    """
    def __init__(self, index_dir):
        _umap = dict(load_uid_map(index_dir))
        # invert uid map
        self._ids = {}
        for key in _umap:
            self._ids[_umap[key]] = key
        self._lexicon = load_lexicon(index_dir)
    
    def __getitem__(self, key):
        return self._lexicon['_' + self._ids[key[2:]]]