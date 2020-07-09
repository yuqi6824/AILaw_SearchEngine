import pandas as pd
from io import BytesIO
import requests
import jieba

def remove_dash(x):
    return x.replace('-', '')

def remove_slash(x):
    return x.replace('/', '，')

def remove_pound(x):
    return x.split('#')[1:]

def to_lower(x):
    return x.lower()

def remove_line_break(x):
    return x.replace('\n', '')

def list_to_str(x):
    return ','.join(x)

def doc_preprocess(dir):
    # load description doc
    data = requests.get(dir).content
    df = pd.read_csv(BytesIO(data))

    # remove dash and slash in doc, and convert all upper to lower
    i = 0
    for col in df:
        i += 1
        if i in (0, 5, 6):
            continue
        df[col] = df[col].astype(str)
        df[col] = df[col].apply(remove_dash)
        df[col] = df[col].apply(remove_slash)
        df[col] = df[col].apply(remove_line_break)
        df[col] = df[col].apply(to_lower)
        i += 1

    # remove the pound in keyword
    df['Keyword'] = df['Keyword'].apply(remove_pound)
    for i in range(len(df['Keyword'])):
        for j in range(len(df['Keyword'][i])):
            df['Keyword'][i][j] = df['Keyword'][i][j].strip()
    df['Keyword'] = df['Keyword'].apply(list_to_str)

    # return a well-process dataframe
    return df

def query_preprocess(query):
    # remove some specific punctuation from query
    query = remove_dash(query)
    query = remove_slash(query)
    query = to_lower(query)

    # remove stopwords from query
    '''
    with open('baidu_stopwords.txt') as file:
        stopwords = set(file.read().splitlines())
    seg_query = jieba.cut_for_search(query)
    final_query = []
    for seg in seg_query:
        if seg not in stopwords:
            final_query.append(seg)

    return ' '.join(final_query)
    '''
    return query