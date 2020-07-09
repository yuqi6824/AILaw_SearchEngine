import whoosh.qparser as qparser
from whoosh.qparser import QueryParser
from text_preprocess import query_preprocess
from collections import defaultdict

def build_search(ix, query):
    # preprocess the query entered by users
    query = query_preprocess(query)

    # create searcher of the index
    searcher = ix.searcher()
    # search the the query in content, title and keyword
    q1 = QueryParser('title', schema=ix.schema, group=qparser.OrGroup).parse(query)
    q2 = QueryParser('keyword', schema=ix.schema, group=qparser.OrGroup).parse(query)
    q3 = QueryParser('content', schema=ix.schema, group=qparser.OrGroup).parse(query)
    r1 = searcher.search(q1, limit=None)
    r2 = searcher.search(q2, limit=None)
    r3 = searcher.search(q3, limit=None)
    results = [r1, r2, r3]

    return results

def execute_search(results):
    res = defaultdict(float)
    # sum up the scores of content, title, keyword to get final rank
    for i in range(len(results)):
        for j in range(len(results[i])):
            if i == 0:
                res[int(dict(results[i][j])['idx'])] += 0.5 * results[i][j].score
            else:
                res[int(dict(results[i][j])['idx'])] += 0.25 * results[i][j].score
    if res:
        res = sorted(res.items(), key=lambda item: item[1], reverse=True)
        final_res = [item[0] for item in res]
        return final_res
    else:
        print('Sorry, we do not find any related contents.')

# test
'''
import whoosh
import pandas as pd
ix = whoosh.index.open_dir('indexdir')
res = build_search(ix, 'H1-B签证取消')
df = pd.read_csv('dataset.csv')
final_res = execute_search(res)
for idx in final_res:
    print(idx, df['Title'][idx].strip('\n'))
'''