# -*- coding: utf-8 -*
import sys
import os
from common_header import headers
import downloadCommits
import downloadIssues
import downloadPulls
import downloadComments
import downloadBaseInfo
import downloadDevelopInfo
import datetime
import getURL
import time
import analyze
import requests
import urllib3
import numpy as np
import urllib
import json
import progress
import threading
import urllib2
import log
def mkdir(path):
    flag = os.path.exists(path)
    if(not flag):
        os.makedirs(path)

def initial(repo):
    try:
        url = 'https://api.github.com/repos/'+repo
        #print(url)
        #如果github上没有该项目则返回1
        #循环获取headers
        header_index = 0
        r = requests.get(url, headers = headers[header_index])
        while(r.status_code==301):
            header_index = header_index + 1
            header_index = header_index % 5
            r = requests.get(url, headers=headers[header_index])
        html = r.text
        data = json.loads(html)
        if('message' in data.keys() and data['message']=='Not Found'):
            return 1
    except BaseException as ex:

        sys.exit()
    try:
        #创建仓库对应的文件夹
        path = './public/data/' + repo + '/'
        mkdir(path)
        #写入创建开始的时间
        with open(path+'/timeStampStart','w') as f:
            timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(timeStamp)
    except:
        sys.exit()
    #获取基础数据
    #new_thread_baseinfo = threading.Thread(target=downloadBaseInfo.downloadBaseInfo, args=(data,url,))
    #new_thread_baseinfo.start()
    #获取develop信息

    try:
        #new_thread_Develop = threading.Thread(target = downloadDevelopInfo.downloadDevelopInfo, args=(data, ))
        #new_thread_Develop.start()
        new_thread_Issues = threading.Thread(target=downloadIssues.downloadIssuesInfo, args=(data,))
        new_thread_Issues.start()
        #new_thread_Pulls = threading.Thread(target=downloadPulls.downloadPullsInfo, args=(data,))
        #new_thread_Pulls.start()
        #new_thread = threading.Thread(target=downloadCommits.downloadCommitInfo, args=(data,))
        #new_thread.start()
    except BaseException as e:
        print(e)

    #下载commits数据
    '''
    new_thread = threading.Thread(target=downloadCommits.getCommit, args=(repo,start,end))
    new_thread.start()
    new_thread = threading.Thread(target=downloadIssues.getIssues, args=(repo, end))
    new_thread.start()
    new_thread = threading.Thread(target=downloadComments.downloadComments, args=(repo, start, end))
    new_thread.start()
    '''
    '''
    progress.progress(repo,"commits","start")
    downloadCommits.getCommit(repo,start,end)
    progress.progress(repo,"commits","end")

    #下载issus数据
    progress.progress(repo,"issues","start")
    downloadIssues.getIssues(repo,end)
    progress.progress(repo,"issues","end")

    progress.progress(repo,"comments","start")
    downloadComments.downloadComments(repo,start,end)
    progress.progress(repo,"comments",'end')
''''''
    progress.progress(repo,"analyze","start")
    analyze.analyze(repo,start,end)
    progress.progress(repo,"analyze",'end')
'''

    with open(path+'/timeStampEnd','w') as f:
        timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(timeStamp)
        f.write(timeStamp)
