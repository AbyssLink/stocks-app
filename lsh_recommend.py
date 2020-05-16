import re
import time

import numpy as np
import pandas as pd
from datasketch import MinHash, MinHashLSHForest

# Number of Permutations
permutations = 128

# Number of Recommendations to return
num_recommendations = 1


# Preprocess will split a string of text into individual tokens/shingles based on whitespace.
def preprocess(text):
    text = re.sub(r'[^\w\s]', '', text)
    tokens = text.lower()
    tokens = tokens.split()
    return tokens


def get_recommendation(title: str, news_list: list):
    df = list_to_df(news_list=news_list)
    forest = get_forest(df, permutations)
    num_recommendations = 10
    # title = 'Coronavirus will infuence finance'
    result = predict(title, df, permutations, num_recommendations, forest)
    if result is not None:
        # return list of dicts
        return result.to_dict('record')
    else:
        return None


def get_forest(data, perms):
    start_time = time.time()

    minhash = []

    for text in data['text']:
        tokens = preprocess(text)
        m = MinHash(num_perm=perms)
        for s in tokens:
            m.update(s.encode('utf8'))
        minhash.append(m)

    forest = MinHashLSHForest(num_perm=perms)

    for i, m in enumerate(minhash):
        forest.add(i, m)

    forest.index()

    print('It took %s seconds to build forest.' % (time.time()-start_time))

    return forest


def predict(text, database, perms, num_results, forest):
    start_time = time.time()

    tokens = preprocess(text)
    m = MinHash(num_perm=perms)
    for s in tokens:
        m.update(s.encode('utf8'))

    idx_array = np.array(forest.query(m, num_results))
    if len(idx_array) == 0:
        return None  # if your query is empty, return none

    result = database.iloc[idx_array]

    print('It took %s seconds to query forest.' % (time.time()-start_time))

    return result


# FIXME: dirty method
def list_to_df(news_list):
    texts = []
    titles = []
    ids = []
    imgs = []
    descriptions = []
    links = []
    dates = []
    for news in news_list:
        texts.append(news.as_dict()['title'] +
                     ' ' + news.as_dict()['description'])
        ids.append(news.as_dict()['id'])
        imgs.append(news.as_dict()['img'])
        titles.append(news.as_dict()['title'])
        descriptions.append(news.as_dict()['description'])
        links.append(news.as_dict()['link'])
        dates.append(news.as_dict()['date'])
    df = pd.DataFrame()
    df['id'] = ids
    df['img'] = imgs
    df['title'] = titles
    df['description'] = descriptions
    df['text'] = texts
    df['link'] = links
    df['date'] = dates
    return df
