import array
import gzip
from re import S

class Postings():
    """
    Inverted Index

    Stores data in array.array of integers
    """
    def __init__(self):
        self.postings = {}
        self.postings_bin = None
        self._doc_lens = {}

    def add_doc_word(self, docid, term_id, count):
        if not term_id in self.postings:
            self.postings[term_id] = array.array('L')
        self.postings[term_id].extend([docid, count])

    def save(self, file, dump_postings=True):
        """
        saves inverted index

        file : string
            target file
        dump_postings : boolean
            if true sets postings to None as it iterates through it in order to save RAM
        """
        # create output array
        table = array.array('L')
        # create index table
        table.append(len(self.postings) + 1)
        table.extend([0 for i in range(len(self.postings) + 1)])
        for id in self.postings:
            table[id + 1] = len(table)
            table.extend(self.postings[id])
            if dump_postings:
                self.postings[id] = None
        table[len(self.postings)] = len(table)
        with open(file, 'wb') as f:
            # f.write(gzip.compress(table, compresslevel=0))
            f.write(table.tobytes())

        
    def read(self, file):
        self.postings = None
        arr = array.array('L')
        with open(file, 'rb') as f:
            # data = gzip.decompress(f.read())
            # arr.frombytes(data)
            arr.frombytes(f.read())
        self.postings_bin = arr

    def get_term(self, id):
        if self.postings != None:
            if id in self.postings:
                return self.postings[id]
            else:
                raise ValueError(f'id: "{id}" is not a term in postings array')
        if self.postings_bin == None:
            raise Exception('postings binary array is not loaded')
        if (id + 1) >= self.postings_bin[0]:
            raise ValueError(f'id: "{id}" is not a term in postings array')
        location = self.postings_bin[id + 1]
        end = self.postings_bin[id + 2]
        return self.postings_bin[location:end]
    
    def get_terms(self):
        if self.postings != None:
            return self.postings
        table = self.postings_bin[0:self.postings_bin[0]]

        return range(0, len(table) - 2)
        
    def parse_postings(self):
        """
        Process postings binary array into dict of arrays
        """
        table = self.postings_bin[0:self.postings_bin[0]]
        self.postings = {}
        for i in range(1, len(table) - 1):
            s = table[i]
            e = table[i + 1]
            # lexicon ids start at zero
            self.postings[i - 1] = self.postings_bin[s:e]

        self.postings_bin = None
    