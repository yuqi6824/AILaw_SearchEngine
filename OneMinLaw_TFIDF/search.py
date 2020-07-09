from sklearn.metrics.pairwise import linear_kernel
from text_preprocess import query_preprocess
from vectorize import vectorize

def search(dir):
    # get the well-trained model and vectors of docs
    tfidf, tfidf_vectors, docs = vectorize(dir)

    # get user's query and preprocess it
    query = input('Please input your search query: ')
    query = [query_preprocess(query)]

    # vectorize the query
    query_vector = tfidf.transform(query)

    # calculate similarity
    cosine_similarities = linear_kernel(query_vector, tfidf_vectors).flatten()
    related_docs_idx = cosine_similarities.argsort()[:-11:-1]
    print('Search Result: ')
    print(docs['Title'].loc[related_docs_idx].to_string())


search('description_doc.csv')
