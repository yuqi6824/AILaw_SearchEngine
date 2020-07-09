#coding:utf-8
from gevent import monkey
monkey.patch_all()

from flask import Flask, request
from gevent.pywsgi import WSGIServer
from search_function import build_search, execute_search
from build_index import build_index
import whoosh
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
import json
import time
import datetime
from flask import Response
import random
from text_preprocess import query_preprocess
from io import BytesIO
import requests

# initialize attributes
app = Flask(__name__,
            static_folder='statics')

data = requests.get(
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vSZ86hc7CtureHiZe8Q3MDvajPsSzWVmHHB0WZ771GzfpMHsIcRiJL6kL4ZRAcOvZhmGRwVTGOhcqHF/pub?gid=1969031769&single=true&output=csv').content
df = pd.read_csv(BytesIO(data))
#df.fillna('N/A')

lawyer_data = requests.get(
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vRgN5OGkz-J-eZINf9b6Dk1ScirGZpnMdTyiy24A-kIuQZzxqQdSgc6Uj4DWYu2Rp7TZIZHGa_OjfKB/pub?gid=1161817469&single=true&output=csv').content
lawyer_info = pd.read_csv(BytesIO(lawyer_data))
#lawyer_info.fillna('N/A')

build_index('https://docs.google.com/spreadsheets/d/e/2PACX-1vSZ86hc7CtureHiZe8Q3MDvajPsSzWVmHHB0WZ771GzfpMHsIcRiJL6kL4ZRAcOvZhmGRwVTGOhcqHF/pub?gid=1969031769&single=true&output=csv')
ix = whoosh.index.open_dir('indexdir')

idx_pwd = '*********'
cache = {}

# common functions
def update():
    global df
    global ix
    global lawyer_info
    global cache
    global data
    global lawyer_data

    data = requests.get(
        'https://docs.google.com/spreadsheets/d/e/2PACX-1vSZ86hc7CtureHiZe8Q3MDvajPsSzWVmHHB0WZ771GzfpMHsIcRiJL6kL4ZRAcOvZhmGRwVTGOhcqHF/pub?gid=1969031769&single=true&output=csv').content
    new_df = pd.read_csv(BytesIO(data))
    #new_df.fillna('N/A')

    lawyer_data = requests.get(
        'https://docs.google.com/spreadsheets/d/e/2PACX-1vRgN5OGkz-J-eZINf9b6Dk1ScirGZpnMdTyiy24A-kIuQZzxqQdSgc6Uj4DWYu2Rp7TZIZHGa_OjfKB/pub?gid=1161817469&single=true&output=csv').content
    new_lawyer_info = pd.read_csv(BytesIO(lawyer_data))
    #new_lawyer_info.fillna('N/A')

    is_updateed_data, is_updated_lawyer = False, False

    # check whether the dataset is updated
    if not df.equals(new_df):
        # clear cache
        cache = {}
        # update the whoosh index file
        df = new_df
        build_index('https://docs.google.com/spreadsheets/d/e/2PACX-1vSZ86hc7CtureHiZe8Q3MDvajPsSzWVmHHB0WZ771GzfpMHsIcRiJL6kL4ZRAcOvZhmGRwVTGOhcqHF/pub?gid=1969031769&single=true&output=csv')
        ix = whoosh.index.open_dir('indexdir')
        is_updateed_data = True
        print('Update dataset and index file successfully!')

    # check whether the lawyer info is updated
    if not lawyer_info.equals(new_lawyer_info):
        lawyer_info = new_lawyer_info
        is_updated_lawyer = True
        print('Update lawyer info successfully!')

def to_upper(x):
    return x.upper()

def create_video_info(idx):
    idx = int(idx)
    video_info = {}

    # add video information
    video_info['video_id'] = idx
    video_info['video_title'] = str(df['Title'][idx]).replace('\n', '')
    video_info['link'] = df['InFrameUrl'][idx]
    video_info['jump_link'] = df['Link'][idx]
    video_info['time_stamp'] = time.mktime(datetime.datetime.strptime(str(df['Date'][idx]), "%m/%d/%Y").timetuple())
    video_info['description'] = str(df['Description'][idx]).replace('\n', '')
    tags = str(df['Keyword'][idx]).upper()
    tags_list = []
    for tag in tags.split('#')[1:]:
        tags_list.append(tag.strip())
    video_info['tags'] = tags_list

    # if the lawyer profile exists, add lawyer information
    if pd.notna(df['LawyerID'][idx]):
        lawyer_id = df['LawyerID'][idx]
        video_info['lawyer_id'] = df['LawyerID'][idx]
        video_info['lawyer_name'] = str(lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Lawyer Name'].values[0])
        video_info['law_firm'] = str(lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Law Firm Name'].values[0])
        video_info['address'] = str(lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Law Firm Address'].values[
            0]).replace('\n', '')
        video_info['number'] = str(lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Contact Number'].values[0])
        video_info['email'] = str(lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Law Firm Email'].values[0])
        video_info['firm_intro'] = \
            str(lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Law Firm Brief Introduction'].values[0]).replace('\n', '')
        video_info['lawyer_intro'] = str(lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)][ \
            'Attorney Brief Introduction (i.e. education history, work experience, licensed state)'].values[0]).replace('\n', '')
        video_info['website'] = \
            str(lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Official Website (if any)'].values[0])
        video_info['location'] = str(lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['location'].values[0])
        video_info['photo'] = str(lawyer_info.loc[lawyer_info['ID'] == lawyer_id]['Profile Photo'].values[0])
        video_info['profile_link'] = str(lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Profile link-stag'].values[0])
    return video_info

# interface
@app.route('/api/tags')
def get_tags():
    tags_set = set([])
    # convert all tags to upper
    tags_col = df['Keyword'].dropna().astype(str).apply(to_upper)
    for tags in tags_col:
        for tag in tags.split('#')[1:]:
            # check whether tag exists
            if tag:
                tags_set.add(tag.strip())
    return Response(json.dumps(sorted(list(tags_set)), ensure_ascii=False), mimetype='application/json')

@app.route('/api/videos')
def search():
    keyword = query_preprocess(request.args.get('keyword', None))
    page = request.args.get('page', None)
    count = request.args.get('count', None)

    # if get page and count arguments, paging the result
    if page or count:
        page, count = int(page), int(count)
        if keyword not in cache:
            res = build_search(ix, keyword)
            result = execute_search(res)
            final_result = []
            if result:
                for idx in result:
                    video_info = create_video_info(idx)
                    final_result.append(video_info)
                cache[keyword] = final_result
                page_result = cache[keyword][page*count: page*count+count]
                return Response(json.dumps(page_result, ensure_ascii=False), mimetype='application/json')
            else:
                return Response(json.dumps([], ensure_ascii=False), mimetype='application/json')
        else:
            if cache[keyword]:
                page_result = cache[keyword][page * count: page * count + count]
                return Response(json.dumps(page_result, ensure_ascii=False), mimetype='application/json')
            else:
                return Response(json.dumps([], ensure_ascii=False), mimetype='application/json')

    # if no page and count arguments, return whole result
    else:
        if keyword not in cache:
            res = build_search(ix, keyword)
            result = execute_search(res)
            final_result = []
            if result:
                for idx in result:
                    video_info = create_video_info(idx)
                    final_result.append(video_info)
                cache[keyword] = final_result
                return Response(json.dumps(cache[keyword], ensure_ascii=False), mimetype='application/json')
            else:
                return Response(json.dumps([], ensure_ascii=False), mimetype='application/json')
        else:
            if cache[keyword]:
                return Response(json.dumps(cache[keyword], ensure_ascii=False), mimetype='application/json')
            else:
                return Response(json.dumps([], ensure_ascii=False), mimetype='application/json')

@app.route('/api/videos/<idx>')
def detail(idx):
    video_info = create_video_info(idx)
    return Response(json.dumps(video_info, ensure_ascii=False), mimetype='application/json')

@app.route('/api/popular-topics')
def popular_topics():
    idx_list = random.sample(range(0, len(df)), 6)
    res = []
    for idx in idx_list:
        video = {}
        video['ID'] = idx
        video['title'] = str(df['Title'][idx]).replace('\n', '')
        res.append(video)
    return Response(json.dumps(res, ensure_ascii=False), mimetype='application/json')

@app.route('/api/idx')
def get_idx():
    pwd = request.args.get('pwd')
    idx_list = [idx for idx, val in df.iterrows()] if str(pwd) == str(idx_pwd) else []
    return Response(json.dumps(idx_list, ensure_ascii=False), mimetype='application/json')

if __name__ == '__main__':
    # create a scheduler to update the system each day
    sched = BackgroundScheduler()
    sched.add_job(update, 'interval', id='update_task', seconds=86400)
    sched.start()
    # start the server
    http_server = WSGIServer(('0.0.0.0', 81), app)
    http_server.serve_forever()