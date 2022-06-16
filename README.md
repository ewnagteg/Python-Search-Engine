# About 

This is a simple search engine implementation I created for MSCI 541. You cfan use it to create a inverted index from a TREC document collection and then you can try running some searches on that index. Unfortunately I can't include the document collection that we used in the course. When I have time I will find one I can link here or just create a small example one. 
Running the engine is not hard, you just need to generate the inverted index before running searches.

# Running

## Generating Inverted Index

For using the search engine you first have to generate the inverted index. 

```
python -m search IndexEngine ./path/to/data.gz ./path/to/outputindex
```


If you want to use the Porter Stemming Algorithm use the --stem option.


```
python -m search IndexEngine ./path/to/data.gz ./path/to/outputindex --stem
```

## Running search program

This command allows you to test out various searchs on using the inverted index that you generated.
```
python -m search search
```

There are no arguments to this. The program will prompt you for further input.

## Retrieval Results

To get retrieval results I have this command:

```
python -m search retrieve BM25 .\indexs-#-nostem\ .\topics.txt ./output.txt runid
```

Arguments
ranker, path_to_index, queries_file, output_file, runname

You can use the --stem (-s) flag to use the Porter Stemmer. You of course have to use a index that has been stemmed for this to work though.

```
python -m search retrieve BM25 .\indexs-#-stem\ .\topics.txt ./output.txt runid --stem
```

## Evaluating Results

You can use the following to generate evaluation of results generated with above command. You need a qrels file for the collection that you generated the index with to run this.
```
python -m search evaltopics .\TRECS.txt .\hw4-bm25-baseline-ewnagteg.txt ./bm25-nostem.csv .\indexs-#-nostem
```

Arguments: qrel, results, output, indexs

# Compatible Python Versions
Any version that is >= 3.7 should work