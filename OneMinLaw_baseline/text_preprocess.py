import pandas as pd
import jieba

def remove_dash(x):
    return x.replace('-', '')

def remove_slash(x):
    return x.replace('/', ' ')

def remove_pound(x):
    return x.replace('#', ',')

def to_lower(x):
    return x.lower()

def slice(x):
    return x[1:]

def doc_preprocess(dir):
    # load description doc
    df = pd.read_csv(dir)

    # remove dash and slash in doc, and convert all upper to lower
    for col in df:
        df[col] = df[col].astype(str)
        df[col] = df[col].apply(remove_dash)
        df[col] = df[col].apply(remove_slash)
        df[col] = df[col].apply(to_lower)

    # remove the pound in keyword
    df['Keyword'] = df['Keyword'].apply(remove_pound)
    df['Keyword'] = df['Keyword'].apply(slice)

    # return a well-process dataframe
    return df

def query_preprocess(query):
    # remove some specific punctuation from query
    query = remove_dash(query)
    query = remove_slash(query)
    query = remove_pound(query)
    query = to_lower(query)

    # remove stopwords from query
    with open('baidu_stopwords.txt') as file:
        stopwords = set(file.read().splitlines())
    seg_query = jieba.cut_for_search(query)
    final_query = []
    for seg in seg_query:
        if seg not in stopwords:
            final_query.append(seg)

    return ' '.join(final_query)