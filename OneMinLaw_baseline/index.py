from text_preprocess import doc_preprocess
from whoosh.index import create_in
from whoosh.fields import *
from jieba.analyse import ChineseAnalyzer
import os

def build_index(dir):
    # load the well-process doc
    df = doc_preprocess(dir)

    # apply jieba chinese analyzer to tokenize the documents
    analyzer = ChineseAnalyzer()

    # create schema, stored = True means can be returned to user
    schema = Schema(idx=ID(stored=True), title=TEXT(stored=True, analyzer=analyzer), author=ID(stored=False),
                    keyword=KEYWORD(analyzer=analyzer), content=TEXT(stored=False, analyzer=analyzer))

    # store the schema information to 'indexdir'
    indexdir = 'indexdir/'
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
    ix = create_in(indexdir, schema)

    # build the index based on schema
    writer = ix.writer()
    for idx, val in df.iterrows():
        writer.add_document(idx=str(idx), title=val[0], author=val[1], keyword=val[2], content=val[3])
    writer.commit()

build_index('description_doc.csv')