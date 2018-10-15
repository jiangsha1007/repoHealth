# -*- coding: utf-8 -*-
import json
from django.db.models import Q
import re
import github
import log
import urllib2
import random
import time
import requests
# 使用了线程库
import threading
from threading import Thread,Lock
# 队列
import queue
import downloadBaseInfo
headers = {
    'User-Agent':'Mozilla/5.0',
    'Authorization': 'token 8f6085fc4cf4b501a7ccad1a3aadc3f98f51384a',
    'Content-Type':'application/json',
    'method': 'GET', 'Accept': 'application/json'}  # 构建请求 request = Request( url, headers=firefox_headers )
class parsePageInfo(threading.Thread):
    def __init__(self, threadName, dataQueue, data):
        super(parsePageInfo, self).__init__()
        # 线程名
        self.threadName = threadName
        # 数据队列
        self.dataQueue = dataQueue
        # 保存解析后数据的文件名
        self.data = data
    def run(self):
        while not PARSE_EXIT:
            try:
                html = self.dataQueue.get(False)
                self.parse(html)
            except:
                pass
    def parse(self, html):

        for i in range(len(html)):  # 遍历获取contributor信息
            try:
                v = html[i]
                pull_id = v['id']
                pull_number = v['number']
                pull_state = v['state']
                if(pull_state=='open'):
                    pull_state = 0
                elif(pull_state=='closed'):
                    pull_state = 1
                else:
                    pull_state = 2
                pull_create_time = v['created_at']
                pull_update_time = v['updated_at']
                pull_closed_time = v['closed_at']
                pull_merged_time = v['merged_at']
                if(pull_merged_time==None):
                    pull_is_merged = 0
                else:
                    pull_is_merged = 1
                pull_user_type = v['author_association']
                pull_user_id = v['user']['id']
                try:
                    user = github.models.User_Org_Info.objects.get(user_id = pull_user_id)
                except github.models.User_Org_Info.DoesNotExist:
                    downloadBaseInfo.getUserInfo(v['user'])
                    user = github.models.User_Org_Info.objects.get(user_id=pull_user_id)
                repo = github.models.Repo_Base_Info.objects.filter(repo_id = self.data['id'])
                try:
                    pulls = github.models.Repo_Pulls_info.objects.get(
                        Q(pull_id=pull_id) & Q(pull_number=pull_number))  # 判断用户或组织是否存在
                    pulls.pull_state = pull_state
                    pulls.pull_update_time = pull_update_time
                    pulls.issue_close_time = pull_closed_time
                    pulls.pull_merged_time = pull_merged_time
                    pulls.pull_is_merged = pull_is_merged
                    pulls.save()

                except github.models.Repo_Pulls_info.DoesNotExist:
                    pulls_new = github.models.Repo_Pulls_info.objects.create(repo=repo[0],
                                                                                user=user,
                                                                              pull_id=pull_id,
                                                                              pull_number=pull_number,
                                                                              pull_create_time=pull_create_time,
                                                                              pull_update_time=pull_update_time,
                                                                              pull_closed_time=pull_closed_time,
                                                                              pull_merged_time = pull_merged_time,
                                                                              pull_is_merged = pull_is_merged,
                                                                             pull_author_association = pull_user_type,
                                                                                pull_state = pull_state   )
                    pulls_new.save()
            except BaseException as e:
                print(e)






class getPageInfo(threading.Thread):
    def __init__(self, threadName, pageQueue , dataQueue,data):
        # threading.Thread.__init__(self)
        # 调用父类初始化方法
        super(getPageInfo, self).__init__()
        # 线程名
        self.threadName = threadName
        # 页码队列
        self.pageQueue = pageQueue
        self.data = data
        # 数据队列
        self.dataQueue = dataQueue
    def run(self):
        try:
            while not CRAWL_EXIT:
                page = self.pageQueue.get(False)
                pulls_url = self.data["pulls_url"][0:-9]+"?state=all"+"&per_page=100&page=" + str(page)
                pulls_html = requests.get(pulls_url, headers=headers).text
                pulls_info = json.loads(pulls_html)
                #把爬下来的数据放到数据队列中
                if (pulls_info):
                    self.dataQueue.put(pulls_info)
        except BaseException as e:
            log.set_log(e)

CRAWL_EXIT = False
PARSE_EXIT = False
def downloadPullsInfo(data):
    # 通过多线程和队列加速爬取速度,分为采集线程和数据处理线程
    # 首先是采集线程
    # 第一步，获取总的页码数量
    pulls_url = data["pulls_url"][0:-9]+"?state=all&per_page=100"
    pulls_Response = requests.get(pulls_url, headers=headers)  # follow
    headData = str(pulls_Response.headers)  # 获取头部信息
    listLink_last_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\"last)', headData)  # 获取最后一页
    # 获取最后一页页码
    if (listLink_last_url and listLink_last_url[0] != ''):
        last_page = re.findall(r'page=([^&#]*)', listLink_last_url[0])
        if (last_page):
            last_page_int = int(last_page[0])
    else:
        last_page_int = 1

    # 第二步，设置页码的队列
    pageQueue = queue.Queue(last_page_int)
    # 第三步，把页数放到页码队列里，先进先出
    for i in range(1, last_page_int + 1):
        pageQueue.put(i)
    # 采集结果(每页的HTML源码)的数据队列，参数为空表示不限制
    dataQueue = queue.Queue()
    # 设置三个采集线程的名字
    crawlList = ["get_tr1", "get_tr2","get_tr3", "get_tr4"]
    # 存储三个采集线程的列表集合
    threadcrawl = []
    for threadName in crawlList:
        thread = getPageInfo(threadName, pageQueue,dataQueue, data)
        thread.start()
        threadcrawl.append(thread)

    # 设置三个解析线程的名字
    parseList = ["parse_tr1", "parse_tr2", "parse_tr3"]
    # 存储三个解析线程
    threadparse = []
    for threadName in parseList:
        thread = parsePageInfo(threadName, dataQueue, data)
        thread.start()
        threadparse.append(thread)

    # 等待pageQueue队列为空，也就是等待之前的操作执行完毕
    while not pageQueue.empty():
        pass
    # 如果pageQueue为空，采集线程退出循环
    global CRAWL_EXIT
    CRAWL_EXIT = True

    for thread in threadcrawl:
        thread.join()

    while not dataQueue.empty():
        pass

    global PARSE_EXIT
    PARSE_EXIT = True

    for thread in threadparse:
        thread.join()
