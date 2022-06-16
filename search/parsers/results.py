from collections import defaultdict
# Author: Eric Nagtegaal modified code by Nimesh Ghelani based on code by Mark D. Smucker
class Result:
    def __init__(self, doc_id, score, rank):
        self.doc_id = doc_id
        self.score = score
        self.rank = rank

    def __lt__(self, x):
        return (self.score, self.doc_id) > (x.score, x.doc_id)

class Results:
    def __init__(self):
        self.query_2_results = defaultdict(list)

    def add_result(self, query_id, result):
        self.query_2_results[query_id].append(result)

    def get_result(self, query_id):
        return self.query_2_results.get(str(query_id), None)

    def sort_results(self, topicid: str):
        self.query_2_results

def parse(filename):
    global_run_id = None
    history = set()
    results = Results()
    with open(filename) as f:
        for line in f:
            line_components = line.strip().split()
            if len(line_components) != 6:
                raise ValueError('lines in results file should have exactly 6 columns')
            query_id, _, doc_id, rank, score, run_id = line_components
            rank = int(rank)
            score = float(score)
        
            if global_run_id is None:
                global_run_id = run_id
            elif global_run_id != run_id:
                raise ValueError('Mismatching runIDs in results file')

            key = query_id + doc_id
            if key in history:
                raise ValueError('Duplicate query_id, doc_id in results file')
            history.add(key)

            results.add_result(query_id, Result(doc_id, score, rank))
    return global_run_id, results
