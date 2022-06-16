import gzip
import re
import os
import json

class GetDoc():
    def __init__(self, wd: str):
        self.wd = wd
        if self.wd[-1] == '/' or self.wd[-1] == '\\':
            self.wd = self.wd[:-1]
        if not os.path.isfile(self.wd + '/uid_map.json.gz'):
            raise FileNotFoundError('Could not find uid_map.json.gz file at {}'.format(self.wd + '/uid_map.json'))
        self.uid_map = {}
        with gzip.open(self.wd + '/uid_map.json.gz', 'rb') as f:
            self.uid_map = json.loads(f.read())

    def get_doc_id(self, uid):
        uid = str(uid)
        if not (uid in self.uid_map):
            raise ValueError(f'Could not find uid: "{uid}" in uid_map')
        docno = self.uid_map[uid]
        ds = docno.split('-')
        datefolder = ds[0][4:] + '/' + ds[0][0:2] + '/' + ds[0][2:4]
        file = self.wd + f'/{datefolder}/{docno}'
        with gzip.open(file + '.json.gz', 'rb') as f:
            file_content = json.loads(f.read())
        return file_content

    def get_doc_docno(self, docno):
        if not re.match('LA\d+-\d+',docno):
            raise ValueError(f'invalid docno: "{docno}"')
        docno = docno[2:] # slice off 'LA'
        ds = docno.split('-')
        datefolder = ds[0][4:] + '/' + ds[0][0:2] + '/' + ds[0][2:4]
        file = self.wd + f'/{datefolder}/{docno}'
        with gzip.open(file + '.json.gz', 'rb') as f:
            file_content = json.loads(f.read())
        return file_content

    def id_to_docno(self, id):
        if id in self.uid_map:
            return 'LA' + self.uid_map[id]
        else:
            raise ValueError(f'id: "{id}" is not in uid_map')
        
    def print_file(self, file):
        print('docno: LA' + file['docno'])
        print('internal id: ' + str(file['uid']))
        print('date: ' + file['date'])
        print('headline: ' + file['headline'])
        print('raw document: ')
        print(file['file'])

        