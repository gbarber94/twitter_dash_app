import pandas as pd
import numpy as np
import requests
from pandas.io.json import json_normalize
import json

def data_pull():

    flatten = lambda l: [item for sublist in l for item in sublist]

    def Getids(url):
        i = 1
        js = []
        while True:
            r = requests.get(url,
            data={'Content-Type':"application/json"},headers = {"PRIVATE-TOKEN":'*********'},
                            params= {'page':i,'per_page':50})
            if r.text == '[]':
                    break
            js.append(json.loads(r.text))
            i += 1
        d = flatten(js)
        df = pd.DataFrame(d)[['id','name']]
        ids = [j['id'] for j in d]
        return ids, df

    def Get_Project_Data(urls,names):
        temp = pd.DataFrame()
        for url,name in zip(urls,names):
            i = 1
            while True:
                r = requests.get(url,data={'Content-Type':"application/json"},headers = {"PRIVATE-TOKEN":'********'},
                                params= {'page':i,'per_page':50})
                if r.text == '[]':
                    break
                each_project = pd.read_json(r.text,orient ='columns')
                each_project['project_name'] = name
                temp = pd.concat([temp,each_project],sort=False)
                i += 1
        return temp

    ids,df = Getids('GROUP URL HERE')
    names = list(df['name'])
    urls_tweets = ['USER URL HERE'.format(i) for i in ids]
    tweets = Get_Project_Data(urls_tweets,names)

    tweets.to_csv('twitter.csv')

# data_pull()
