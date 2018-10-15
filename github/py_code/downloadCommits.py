# -*- coding: utf-8 -*-
import json
import re
import github
import log
import urllib2
import requests
import threading
from threading import Thread,Lock
# 队列
import queue
headers = {
    'User-Agent':'Mozilla/5.0',
    'Authorization': 'token 8f6085fc4cf4b501a7ccad1a3aadc3f98f51384a',
    'Content-Type':'application/json',
    'method': 'GET', 'Accept': 'application/json'}  # 构建请求 request = Request( url, headers=firefox_headers )
class parsePageInfo(threading.Thread):
    def __init__(self, threadName, itemQueue, data):
        super(parsePageInfo, self).__init__()
        # 线程名
        self.threadName = threadName
        # 数据队列
        self.itemQueue = itemQueue
        # 保存解析后数据的文件名
        self.data = data
    def run(self):
        while not PARSE_EXIT:
            try:
                i = self.itemQueue.get(False)
                self.parse(i)
            except:
                pass
    def parse(self, i):
            try:
                global commit_activity_info
                global commit_activity_arr

                v = commit_activity_info[i]
                week = v['week']
                commit_activity_arr[week] = v['total']


            except BaseException as e:
                set_log(e)
class parsePageInfo2(threading.Thread):
    def __init__(self, threadName, itemQueue2, data):
        super(parsePageInfo2, self).__init__()
        # 线程名
        self.threadName = threadName
        # 数据队列
        self.itemQueue = itemQueue2
        # 保存解析后数据的文件名
        self.data = data
    def run(self):
        while not PARSE_EXIT2:
            try:
                i = self.itemQueue.get(False)
                self.parse(i)
            except:
                pass
    def parse(self, i):
            try:
                global code_frequency_info
                global code_frequency_add_arr
                global code_frequency_delete_arr
                v = code_frequency_info[i]
                week = v[0]
                code_frequency_add_arr[week] = v[1]
                code_frequency_delete_arr[week] = v[2]

            except BaseException as e:
                set_log(e)
PARSE_EXIT = False
global commit_activity_arr
commit_activity_arr = {}
PARSE_EXIT2 = False
global code_frequency_add_arr
code_frequency_add_arr = {}
global code_frequency_delete_arr
code_frequency_delete_arr = {}
#过去一年commit提交情况
def get_commit_activity(data):
    #第一步，获取页面数据

    commit_activity_url = data["url"] + "/stats/commit_activity"
    commit_activity_html = requests.get(commit_activity_url, headers=headers).text
    global commit_activity_info

    commit_activity_info = json.loads(commit_activity_html)
    # 第二步，设置项数的队列
    itemQueue = queue.Queue(len(commit_activity_info))
    for i in range(0, len(commit_activity_info) ):
        itemQueue.put(i)
    # 设置三个解析线程的名字
    parseList = ["parse_tr1", "parse_tr2", "parse_tr3"]
    # 存储三个解析线程
    threadparse = []
    for threadName in parseList:
        thread = parsePageInfo(threadName, itemQueue, data)
        thread.start()
        threadparse.append(thread)
    while not itemQueue.empty():
        pass

    global PARSE_EXIT
    PARSE_EXIT = True

    for thread in threadparse:
        thread.join()
#过去一年commit提交情况
def get_code_frequency(data):
    try:
        #第一步，获取页面数据
        code_frequency_url = data["url"] + "/stats/code_frequency"
        code_frequency_html = requests.get(code_frequency_url, headers=headers).text
        global code_frequency_info

        code_frequency_info = json.loads(code_frequency_html)
        # 第二步，设置项数的队列
        itemQueue2 = queue.Queue(len(code_frequency_info))
        for i in range(0, len(code_frequency_info) ):
            itemQueue2.put(i)
        # 设置三个解析线程的名字
        parseList = ["parse2_tr1", "parse2_tr2", "parse2_tr3"]
        # 存储三个解析线程
        threadparse = []
        for threadName in parseList:
            thread = parsePageInfo2(threadName, itemQueue2, data)
            thread.start()
            threadparse.append(thread)
        while not itemQueue2.empty():
            pass


        global PARSE_EXIT2
        PARSE_EXIT2 = True

        for thread in threadparse:
            thread.join()
    except BaseException as e:
        set_log(e)

def downloadCommitInfo(data):
    new_thread = threading.Thread(target=get_commit_activity, args=(data,))
    new_thread.start()

    new_thread2 = threading.Thread(target=get_code_frequency, args=(data,))
    new_thread2.start()
    new_thread.join()
    new_thread2.join()
    try:
        repo = github.models.Repo_Base_Info.objects.filter(repo_id=data['id'])
        if(repo):
            commit = github.models.Repo_Develop_info.objects.filter(repo=repo[0])
            if(commit and len(commit)>0):
                commit[0].commit_count_perweek_lastyear = json.dumps(commit_activity_arr, ensure_ascii=False, encoding='UTF-8')
                commit[0].code_add_count_perweek = json.dumps(code_frequency_add_arr, ensure_ascii=False, encoding='UTF-8')
                commit[0].code_delete_count_perweek = json.dumps(code_frequency_delete_arr, ensure_ascii=False, encoding='UTF-8')
                commit[0].save()
            else:
                commit_new = github.models.Repo_Develop_info.objects.create(repo=repo[0],
                                                                            commit_count_perweek_lastyear = json.dumps(commit_activity_arr, ensure_ascii=False, encoding='UTF-8'),
                                                                            code_add_count_perweek = json.dumps(code_frequency_add_arr, ensure_ascii=False, encoding='UTF-8'),
                                                                            code_delete_count_perweek = json.dumps(code_frequency_delete_arr, ensure_ascii=False, encoding='UTF-8'),
                                                                            )
                commit_new.save()
    except BaseException as e:
        set_log(e)

def set_log(e):
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s"
    logging.basicConfig(format=LOG_FORMAT)
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    fh = logging.FileHandler('error.log')
    fh.setFormatter(LOG_FORMAT)
    logger.addHandler(fh)
    logger.error(e)
