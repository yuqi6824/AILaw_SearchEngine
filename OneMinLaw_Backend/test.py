import pandas as pd
import json
import whoosh
from search_function import build_search, execute_search
import pandas as pd
import time
import datetime
import requests
from io import BytesIO

data = requests.get(
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vSZ86hc7CtureHiZe8Q3MDvajPsSzWVmHHB0WZ771GzfpMHsIcRiJL6kL4ZRAcOvZhmGRwVTGOhcqHF/pub?gid=1969031769&single=true&output=csv').content
df = pd.read_csv(BytesIO(data))

def to_upper(x):
    return x.upper()

def get_tags():
    tags_set = set([])
    tags_col = df['Keyword'].dropna().astype(str).apply(to_upper)
    for tags in tags_col:
        for tag in tags.split('#')[1:]:
            if tag:
                print(tag.strip())
                tags_set.add(tag.strip())
    print(len(tags_set))
    return json.dumps(sorted(list(tags_set)), ensure_ascii=False)

ix = whoosh.index.open_dir('indexdir')
df = pd.read_csv('dataset.csv')
lawyer_info = pd.read_csv('lawyer_profile.csv')

def test_search(search_word):
    res = build_search(ix, search_word)
    result = execute_search(res)
    final_result = []
    if result:
        for idx in result:
            video_info = {}
            video_info['video_id'] = idx
            video_info['video_title'] = df['Title'][idx].strip('\n')
            video_info['link'] = df['InFrameUrl'][idx]
            video_info['time_stamp'] = time.mktime(datetime.datetime.strptime(df['Date'][idx], "%m/%d/%Y").timetuple())
            tags = str(df['Keyword'][idx]).upper()
            tags_list = []
            for tag in tags.split('#')[1:]:
                tags_list.append(tag.strip())
            video_info['tags'] = tags_list
            if pd.notna(df['LawyerID'][idx]):
                lawyer_id = df['LawyerID'][idx]
                video_info['lawyer_id'] = df['LawyerID'][idx]
                video_info['lawyer_name'] = lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Lawyer Name'].values[0]
                video_info['law_firm'] = lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Law Firm Name'].values[0]
                video_info['address'] = lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Law Firm Address'].values[0].strip('\n')
                video_info['number'] = lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Contact Number'].values[0]
                video_info['email'] = lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Law Firm Email'].values[0]
                video_info['firm_intro'] = lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Law Firm Brief Introduction'].values[0].strip('\n')
                video_info['lawyer_intro'] = lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Attorney Brief Introduction (i.e. education history, work experience, licensed state)'].values[0].strip('\n')
                video_info['area'] = lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Practice Area/Specialty Case Types'].values[0]
                video_info['website'] = lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['Official Website (if any)'].values[0]
                video_info['location'] = lawyer_info.loc[(lawyer_info['ID'] == lawyer_id)]['location'].values[0]
            print(video_info)
            print('--------------------------------')
            final_result.append(video_info)
        return json.dumps(final_result, ensure_ascii=False)

print(test_search('opt'))