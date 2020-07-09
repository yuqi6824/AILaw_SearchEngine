import math
import pandas as pd
from vectorize import vectorize
from text_preprocess import query_preprocess
from scipy import spatial

def calculate_dcg(items):
    dcg = 0
    i = 0
    for item in items:
        i += 1
        dcg += item / math.log(i + 1, 2)
    return dcg

# load the tfidf vectorizer and the tfidf vector of docs
tfidf, tfidf_vectors, docs = vectorize('description_doc.csv')

# load the query list and true score of rankings
relevance = pd.read_csv('relevance.csv')
test_query = relevance.columns.values[1:]
true_score = []
for col in relevance:
    true_score.append(relevance[col].tolist())
true_score = true_score[1:]

# preprocess the query in query list
query_list = []
for query in test_query:
    query_list.append([query_preprocess(query)])

# convert the query to vector
query_vectors = []
for query in query_list:
    query_vectors.append(tfidf.transform(query).toarray()[0])

# construct vector list for docs
dv = tfidf_vectors.toarray()
doc_vectors = [dv[i] for i in range(len(dv))]

# get the similarity of between each query and doc
res = []
for i in range(len(query_vectors)):
    tmp = []
    for j in range(len(doc_vectors)):
        tmp.append([j, 1 - spatial.distance.cosine(query_vectors[i], doc_vectors[j])])
    res.append(tmp)

# sort the result of search of each query
for i in range(len(res)):
    res[i] = sorted(res[i], key=lambda x: x[1], reverse=True)

# assign the score to the res list
rel_score = []
for i in range(len(res)):
    tmp = []
    for j in range(len(res[i])):
        tmp.append(true_score[i][res[i][j][0]])
    rel_score.append(tmp)
print(rel_score)

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