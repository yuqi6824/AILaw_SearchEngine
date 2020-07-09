from text_preprocess import doc_preprocess
import gensim
import jieba

with open('baidu_stopwords.txt') as file:
    stopword = file.read().splitlines()
docs = doc_preprocess('description_doc.csv')
doc_list = []
for idx, val in docs.iterrows():
    doc_list.append(' '.join(val))
seg_doc = [jieba.cut_for_search(doc) for doc in doc_list]
processed_doc = []
tmp = []
for seg in seg_doc:
    for word in seg:
        if word not in stopword:
            tmp.append(word)
    processed_doc.append(tmp)
    tmp = []
processed_doc = [','.join(processed_doc[i]) for i in range(len(processed_doc))]

pretrain_model = gensim.models.Word2Vec.load('word2vec_wiki.model')
print(pretrain_model.wv.vectors.shape)
pretrain_model.build_vocab(processed_doc, update=True)
pretrain_model.train(processed_doc, total_examples=len(processed_doc), epochs=pretrain_model.epochs)
print(pretrain_model.wv.vectors.shape)
print(pretrain_model)

