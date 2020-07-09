from text_preprocess import doc_preprocess
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def vectorize(dir):
    # load doc and preprocess it
    docs = doc_preprocess(dir)

    with open('baidu_stopwords.txt') as file:
        stopword = set(file.read().splitlines())

    # build doc list
    doc_list = []
    for idx, val in docs.iterrows():
        doc_list.append(' '.join(val))

    # tokenize the doc
    seg_doc = [jieba.cut_for_search(doc) for doc in doc_list]

    # remove stopwords
    processed_doc = []
    tmp = []
    for seg in seg_doc:
        for word in seg:
            if word not in stopword:
                tmp.append(word)
        processed_doc.append(tmp)
        tmp = []
    processed_doc = [' '.join(processed_doc[i]) for i in range(len(processed_doc))]

    # vectorize the doc list
    tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 3)).fit(processed_doc)
    tfidf_vectors = tfidf.transform(processed_doc)

    return tfidf, tfidf_vectors, docs