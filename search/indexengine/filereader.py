import gzip
import os
import re
import json
from pathlib import Path
from search.indexengine.invertedindex import Postings
from search.indexengine.porter import PorterStemmer, stem_doc
from search.lib.funcs import convert_date
from search.indexengine.processedfile import ProcessedFile
from search.indexengine.tokenizer import *

class UID():
    def __init__(self):
        self.id = 0

    def next(self):
        self.id += 1
        return self.id + 1

class ProcessData():
    """
    Creates metadata and inverted index
    """
    def __init__(self, file, outdir):
        self.file = file
        self.outdir = outdir
        self._docno_regex = re.compile('<DOCNO>\s+LA\d+-\d+\s+</DOCNO>')
        self.uid = UID()
        self.uid_map = {}
        self.lexicon = {}
        self.lexicon['_tokens'] = 0
        self.postings = Postings()
        self._postings_file = 'postings.bin'
        self._lexicon_file = 'lexicon.json.gz'
        self._uid_file = 'uid_map.json.gz'
        self._porter = PorterStemmer()
        self._total = 0
        self._N = 0
        self._stem_cache = {}

    def read(self, save_metadata=True, use_stemmer=False):
        current_file = ''
        start_tag = re.compile('(.*?)<DOC\>(.*?)')
        end_tag = re.compile('(.*?)</DOC>(.*?)')
        with gzip.open(self.file, 'rt') as f:
            for line in f:
                current_file += line
                if end_tag.match(line):
                    self.process_file(current_file, save_metadata, use_stemmer)
                    current_file = ''
        if save_metadata:
            self.dump_uid_map()
            self._save()
        # allows us to only create postings file
        if not save_metadata:
            self.postings.save(self.outdir + '/' + self._postings_file)


    def process_file(self, file, save_metadata, use_stemmer):
        processed_file = ProcessedFile(file, self.uid.next())
        self._extract_meta(file, processed_file)
        self.uid_map[processed_file.data['uid']] = processed_file.data['docno']
        self._add_to_postings(processed_file, use_stemmer)
        if save_metadata:
            self._save_file(processed_file)

    def _extract_meta(self, file: str, processed_file: ProcessedFile):
        docno = ['', '']
        date = ''
        headline = ''
        graphic = ''
        scan = ''
        scanning = False
        graphic_re = re.compile('(.*?)<GRAPHIC>(.*?)')
        graphic_end_re = re.compile('(.*?)</GRAPHIC>(.*?)')
        text_tag_re = re.compile('(.*?)<TEXT>(.*?)')
        text_end_tag_re = re.compile('(.*?)</TEXT>(.*?)')
        headline_regex = re.compile('(.*?)<HEADLINE>(.*?)')
        text = ''
        textscan = ''
        scantext = False
        for line in file.split('\n'):
            if not scanning:
                # docno should be on one line eg <DOCNO> docno </DOCNO>
                if self._docno_regex.match(line):
                    docno = re.findall('\d+-\d+', line)[0].split('-')
                elif headline_regex.match(line):
                    scanning = True
                elif graphic_re.match(line):
                    scanning = True
                elif text_tag_re.match(line):
                    scantext = True
            if scanning:  # not else to avoid edge case where end tag is on same line
                if re.match('(.*?)</HEADLINE>(.*?)', line):
                    headline = scan + ' ' + line if scan != '' else line 
                    scan = ''
                    scanning = False
                elif graphic_end_re.match(line):
                    graphic += scan + ' ' + line if scan != '' else line 
                    scan = ''
                    scanning = False
                else:
                    scan += line
            elif text_end_tag_re.match(line):
                text = textscan + ' ' + line if textscan != '' else line 
                scantext = False      
            if scantext:
                textscan += line
        if docno[0] != 0:
            # delete tags in headline
            headline = re.sub('<[^<]*>','', headline)
            date = convert_date('19' + docno[0][4:], docno[0][0:2], docno[0][2:4])
            processed_file.date_folder = '{}/{}/{}'.format(docno[0][4:], docno[0][0:2], docno[0][2:4])
            processed_file.set_meta(
                '{}-{}'.format(docno[0], docno[1]), headline, date, graphic, file, text)
        else:
            raise ValueError('Could not parse DOCNO')

    def _add_to_postings(self, processed_file: ProcessedFile, use_stemmer):
        docid = processed_file.data['uid']
        file = processed_file.data['file']
       
        text = '{} {} {}'.format(
            processed_file.data['headline'],
            processed_file.text,
            processed_file.data['graphic']
        )
        text = remove_tags(text)
        tokens = tokenize(text)
        if use_stemmer:
            tokens = self._stem_tokens(tokens)
        token_ids = convert_tokens_to_ids(tokens, self.lexicon)
        word_counts = count_words(token_ids)
        add_to_postings(word_counts, docid, self.postings)
        self.lexicon['_' + str(docid)] = len(list(token_ids))
        self._total += self.lexicon['_' + str(docid)]
        self._N += 1
    
    def _save(self):
        # store extra data in lexicon
        self.lexicon['_avdl'] = self._total / self._N
        self.lexicon['_N'] = self._N

        with open(self.outdir + '/' + self._lexicon_file, 'wb') as outfile:
            outfile.write(
                gzip.compress(bytes(json.dumps(self.lexicon), 'utf-8'))
            )
        self.postings.save(self.outdir + '/' + self._postings_file)

    def get_postings(self):
        self.postings.read(self.outdir + '/' + self._postings_file)

    def dump_uid_map(self):
        with open(self.outdir + '/' + self._uid_file, 'wb') as outfile:
            outfile.write(
                gzip.compress(bytes(json.dumps(self.uid_map), 'utf-8'))
            )

    def check_dir(self, outdir):
        return not os.path.isdir(outdir)

    def check_file(self, gzfile):
        return os.path.isfile(gzfile)

    def _save_file(self, processed_file: ProcessedFile):
        # create path if it doesn't exist
        target_dir = self.outdir + '/' + processed_file.date_folder+ '/'
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        with open(target_dir + processed_file.data['docno'] + '.json.gz', 'wb') as outfile:
            data = bytes(json.dumps(processed_file.data), 'utf-8')
            outfile.write(
                gzip.compress(data)
            )
    
    def _stem(self, token):
        if token in self._stem_cache:
            return self._stem_cache[token]
        stem = self._porter.stem(token, 0,len(token)-1)
        self._stem_cache[token] = stem
        return stem

    def _stem_tokens(self, tokens):
        return map(
            self._stem, 
            tokens
        )