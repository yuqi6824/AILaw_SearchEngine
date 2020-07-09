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
    schema = Schema(idx=ID(stored=True), title=TEXT(stored=True, analyzer=analyzer),
                    keyword=KEYWORD(analyzer=analyzer), content=TEXT(stored=False, analyzer=analyzer))

    # store the schema information to 'indexdir'
    indexdir = 'indexdir/'
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
    ix = create_in(indexdir, schema)

    # build the index based on schema
    writer = ix.writer()
    for idx, val in df.iterrows():
        writer.add_document(idx=str(idx), title=str(val[0]), keyword=val[5], content=str(val[6]))
    writer.commit()

'''
build_index(
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vSZ86hc7CtureHiZe8Q3MDvajPsSzWVmHHB0WZ771GzfpMHsIcRiJL6kL4ZRAcOvZhmGRwVTGOhcqHF/pub?gid=1969031769&single=true&output=csv')
'''
