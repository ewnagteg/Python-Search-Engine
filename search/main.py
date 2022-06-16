import sys
from search.evaluation.evaluation import evaluate_results_topics
from search.indexengine.filereader import *
import argparse
from search.lib.funcs import TokenCounts
from search.retrieve.bm25 import BM25
from search.retrieve.cos import Cos
from search.retrieve.topics import *
from search.retrieve.booleanand import *
import search.search_tool as search_tool

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('program', type=str, help='Specify which program to run IndexEngine, or search', 
        choices=['IndexEngine', 'search', 'retrieve', 'evaltopics'])

    args = parser.parse_args(sys.argv[1:2])

    if args.program == 'IndexEngine':
        rf = ProcessData('./test-docs.gz', './text-index-#')
        parser = argparse.ArgumentParser()
        # path to input file
        parser.add_argument('path_to_latimes', type=str, help='path to latimes.gz file')
        parser.add_argument('path_to_output', type=str, help='output directory path')
        parser.add_argument('--stem', '-s', dest='stem', action='store_true', help='use stemmer')
        parser.set_defaults(stem=False)
        args = parser.parse_args(sys.argv[2:])

        rf = ProcessData(args.path_to_latimes, args.path_to_output)
        rf.read(save_metadata=True, use_stemmer=args.stem)
    elif args.program=='search':
        parser = argparse.ArgumentParser()
        parser.add_argument('path_to_index', type=str, help='path to index')
        args = parser.parse_args(sys.argv[2:])
        search_tool.main(args.path_to_index)
    elif args.program == 'evaltopics':
        parser = argparse.ArgumentParser()
        parser.add_argument('qrel', type=str, help='qrel file')
        parser.add_argument('results', type=str, help='path to results file')
        parser.add_argument('output', type=str, help='path to output file')
        parser.add_argument('indexs', type=str, help='path to token counts file')
        args = parser.parse_args(sys.argv[2:])

        token_counts = TokenCounts(args.indexs)
        evaluate_results_topics(args.qrel, args.output, args.results, token_counts)
    elif args.program == 'retrieve':
        parser = argparse.ArgumentParser()
        # path to input file
        parser.add_argument('ranker', type=str, help='Ranking algorithm, either booleanAND (and) BM25 or Cos', choices=['and', 'BM25', 'Cos'])
        parser.add_argument('path_to_index', type=str, help='path to index')
        parser.add_argument('queries_file', type=str, help='queries file')
        parser.add_argument('output_file', type=str, help='file to write output to')
        parser.add_argument('runname', type=str, help='run name to use')
        parser.add_argument('--stem', '-s', dest='stem', action='store_true', help='use stemmer')
        parser.set_defaults(stem=False)
        args = parser.parse_args(sys.argv[2:])
        ret = None
        if args.ranker=='and':
            ret = BooleanAnd(args.path_to_index)
        elif args.ranker=='BM25':
            ret = BM25(args.path_to_index)
        elif args.ranker=='Cos':
            ret = Cos(args.path_to_index)
        ret.load_postings()
        ret.load_lexicon()
        topics = Topics(args.queries_file, args.path_to_index)
        topics.search_topics(ret, args.output_file, args.runname, stem=args.stem)

