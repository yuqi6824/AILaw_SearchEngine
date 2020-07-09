import whoosh.index as index
import whoosh.qparser as qparser
from whoosh.qparser import QueryParser
from text_preprocess import query_preprocess
from collections import defaultdict

def build_search(dir, query):
    # preprocess the query entered by users
    query = query_preprocess(query)

    # import the created index
    ix = index.open_dir(dir)

    # create searcher of the index
    searcher = ix.searcher()

    # search the the query in content, title and keyword
    q1 = QueryParser('content', schema=ix.schema, group=qparser.OrGroup).parse(query)
    q2 = QueryParser('title', schema=ix.schema, group=qparser.OrGroup).parse(query)
    q3 = QueryParser('keyword', schema=ix.schema, group=qparser.OrGroup).parse(query)
    r1 = searcher.search(q1, limit=None)
    r2 = searcher.search(q2, limit=None)
    r3 = searcher.search(q3, limit=None)

    return [r1, r2, r3]

def execute_search():
    query = input('Please enter your search query: ')
    results = build_search('indexdir', query)
    res = defaultdict(float)
    # sum up the scores of content, title, keyword to get final rank
    for i in range(len(results)):
        for j in range(len(results[i])):
            res[str(results[i][j])] += results[i][j].score
    if res:
        res = sorted(res.items(), key=lambda item: item[1], reverse=True)
        for r in res:
            print(int(r[0].split("'")[3]))
            print(r[0], r[1])
    else:
        print('Sorry, we do not find any related contents.')

execute_search()