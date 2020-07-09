import whoosh.index as index
import whoosh.qparser as qparser
from whoosh.qparser import QueryParser
from text_preprocess import query_preprocess
from collections import defaultdict
import pandas as pd
from text_preprocess import query_preprocess
import math

def calculate_dcg(items):
    dcg = 0
    i = 0
    for item in items:
        i += 1
        dcg += item / math.log(i + 1, 2)
    return dcg

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

# load the query list and true score of rankings
relevance = pd.read_csv('relevance.csv')
test_query = relevance.columns.values[1:]
true_score = []
for col in relevance:
    true_score.append(relevance[col].tolist())
true_score = true_score[1:]

# search
results_list = []
for query in test_query:
    results = build_search('indexdir', query)
    res = defaultdict(float)
    # sum up the scores of content, title, keyword to get final rank
    for i in range(len(results)):
        for j in range(len(results[i])):
            res[str(results[i][j])] += results[i][j].score
    res = sorted(res.items(), key=lambda item: item[1], reverse=True)
    tmp = []
    for r in res:
        tmp.append(int(r[0].split("'")[3]))
    results_list.append(tmp)

for i in range(len(results_list)):
    for j in range(45):
        if j not in results_list[i]:
            results_list[i].append(j)

# assign the score to the res list
rel_score = []
for i in range(len(results_list)):
    tmp = []
    for j in range(len(results_list[i])):
        tmp.append(true_score[i][results_list[i][j]])
    rel_score.append(tmp)

# calculate dcg, idcg and ndcg
dcg = []
idcg = []

for i in range(len(rel_score)):
    dcg.append(calculate_dcg(rel_score[i]))

perfect_score = []
for i in range(len(rel_score)):
    perfect_score.append(sorted(rel_score[i], reverse=True))

for i in range(len(perfect_score)):
    idcg.append(calculate_dcg(perfect_score[i]))

ndcg_list = []
for i in range(len(dcg)):
    ndcg_list.append(dcg[i]/idcg[i])

ndcg = sum(ndcg_list) / len(ndcg_list)

print('NDCG for each query:' + '\n' + str(ndcg_list) + '\n')
print ('Average NDCG: %f' % ndcg)