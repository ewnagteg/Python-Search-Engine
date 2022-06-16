from os import remove
import re
from search.indexengine.tokenizer import tokenize, remove_tags
from search.indexengine.porter import PorterStemmer, stem_doc
from search.getdoc.getdoc import GetDoc
import traceback
import sys

        
class Topics():
    """
    Used for parsing and handleing topics file
    """
    def __init__(self, topics_file, path_to_index):
        self._topics_file = topics_file
        self.getdoc = GetDoc(path_to_index)
        self._porter = PorterStemmer()

    def search_topics(self, query, output_file, runname, include_doc=False, topics_subset=None, limit_size=None, stem=False, output=None):
        """
        Runs boolean and retrieval for every topic file

        query : BooleanAnd
            Boolean AND object for running retrieval
        output_file : string 
            Where to save output to, if already exists, will overwrite
        include_doc : boolean
            If set to true will include document text in output, will also format output to be easy to read (markdown format)
        topics_subset : list
            can be used to only use subset of topics in topics document, eg for q3 you can do topics_subset=[401, 403]
        limit_size : integer
            Limits result list of docs to given limit
        stem : boolean
            Whether to use porter stemmer on query, default False
        """
        if output == None:
            output = open(output_file, 'wt')
        with open(self._topics_file, 'rt') as file:
            current_topicid = ''
            for line in file:
                try:
                    if re.match('<num>.*', line):
                        current_topicid = int(re.findall('\d+', line)[0])
                        if include_doc:
                            if current_topicid in topics_subset if topics_subset != None else True:
                                output.write(f'\n\n\n# {current_topicid}\n')
                    elif re.match('<title>.*', line):
                        query_text = remove_tags(line)
                        if stem:
                            query_text = stem_doc(self._porter, query_text)
                        if current_topicid in topics_subset if topics_subset != None else True:
                            if not include_doc:
                                self.run_query(query, query_text, runname, current_topicid, output, limit_size=limit_size)
                            else:
                                self._pretty_query(query, query_text, runname, current_topicid, output, limit_size=limit_size)

                except Exception as e:
                    print(f'Got exception when parsing line: "{line}"')
                    print(e)
                    traceback.print_exception(*sys.exc_info())

        output.close()

    def run_query(self, query, query_text, runname, topicid, output, limit_size=None):
        result = query.query(query_text)
        if limit_size != None:
            result = result[:limit_size]
        if len(result) == 0:
            print(f'No result for topic: {topicid} query: {query_text}')
        for i in range(len(result)):
            docno = self.getdoc.id_to_docno(str(result[i][0]))

            # create query id by tokenizing and sorting tokens
            tokens = list(tokenize(query_text))
            tokens.sort()
            output.write('{} Q0 {} {} {} {}'.format(
                topicid,
                docno,
                i + 1, # rank
                result[i][1], # score
                runname
            ) + '\n')
    
    def _pretty_query(self, query, query_text, runname, topicid, output, limit_size=None):
        result = query.query(query_text)
        if limit_size != None:
            result = result[:limit_size]
        for i in range(len(result)):
            docno = self.getdoc.id_to_docno(str(result[i][0]))

            # create query id by tokenizing and sorting tokens
            tokens = list(tokenize(query_text))
            tokens.sort()
            query_id = '&'.join(tokens)
            output.write(f'## Topic: {topicid}  Rank: {i+1}\t\t{query_text}\n')
            output.write('{} q0 {} {} {} {}'.format(
                topicid,
                docno,
                i + 1, # rank
                result[i][1], # score
                runname
            ) + '\n')
            output.write('### Document\n\n')

            # make doc easier to read
            doctext = self.getdoc.get_doc_docno(docno)['file']
            doctext = re.sub('<.?P>', '', doctext)
            doctext = re.sub('\n{3}', '\n', doctext)

            # making terms into tags makes Vscode highlight them differently making them easier to see
            for term in tokens:
                doctext = re.sub(f'[^a-zA-Z0-9]{term}[^a-zA-Z0-9]', f' <{term.upper()}> ', doctext, flags=re.I)
            output.write(doctext)
            output.write('\n\n')



        