from search.evaluation.mean import average_precision, mean_average_precision
from search.evaluation.ndgc import mean_ndcg, ndcg
from search.evaluation.tbg import mean_tbg, tbg
from search.parsers import results
from search.parsers.qrels import Qrels, parse_qrels
from search.parsers.results import Results, parse
import traceback
import os
import re
def evaluate_results(qrel_path: str, output_file: str, results_dir: str, token_counts, verbose=False):
    qrel = parse_qrels(qrel_path)
    with open(output_file, 'wt') as o:
        o.write('Run Name,Average Percision,Precision@10,NDGC@10,NDGC@1000,Time-biased gain\n')
        files = os.listdir(results_dir)
        files = filter(lambda file: re.match(r'.*\.results', file), files)
        for file in files:
            filepath = ''
            run_id, result = (0, 0)
            parsed = False
            try:
                filepath = f'{results_dir}/{file}'
                run_id, result = parse(filepath)
                parsed = True
            except Exception as e:
                print(f'Failed to parse results from "{filepath}"')
                if verbose:
                    print(e)
                    traceback.print_exc()
            if parsed:
                try:
                    o.write(run_id + ',')
                    o.write(str(mean_average_precision(qrel, result)) + ',')
                    o.write(str(mean_average_precision(qrel, result, limit=10)) + ',')
                    o.write(str(mean_ndcg(qrel, result, 10)) + ',')
                    o.write(str(mean_ndcg(qrel, result, 1000)) + ',')
                    o.write(str(mean_tbg(qrel, result, token_counts)))
                    o.write('\n')
                except Exception as e:
                    o.write('\n')
                    print(f'Failed on "{filepath}"')
                    print(e)
                    traceback.print_exc()

def evaluate_results_topics(qrel_path: str, output_file: str, results_file: str, token_counts):
    qrel = parse_qrels(qrel_path)
    with open(output_file, 'wt') as o:
        run_id, result = parse(results_file)
        o.write('Query id,Average Precision,Precision@10,NDGC@10,NDGC@1000,Time-biased gain\n')
        for queryid in qrel.get_query_ids(): 
            # stops it from breaking when missing query (like msmucker's)
            if result.get_result(queryid) != None:
                try:
                    o.write(f'{queryid},')
                    o.write(f'{average_precision(qrel, result, queryid)},')
                    o.write(f'{average_precision(qrel, result, queryid, limit=10)},')
                    o.write(f'{ndcg(qrel, result, queryid, limit=10)},')
                    o.write(f'{ndcg(qrel, result, queryid, limit=1000)},')
                    o.write(f'{tbg(qrel, result, queryid, token_counts)}')
                    o.write('\n')
                except Exception as e:
                    print('Failed on "{queryid}" with "{result.doc_id}"')
                    print(e)
                    traceback.print_exc()