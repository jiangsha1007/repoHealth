# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
import sys
from py_code import initial
from py_code import downloadIssues
from py_code import log
import json
from django.db.models import Q
import re
import github

import urllib2
import random
import time
import requests
# 使用了线程库
import threading
from threading import Thread,Lock
# 队列
import queue
# Create your views here.
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Authorization': 'token 8f6085fc4cf4b501a7ccad1a3aadc3f98f51384a',
    'Content-Type': 'application/json',
    'method': 'GET', 'Accept': 'application/json'}  # 构建请求 request = Request( url, headers=firefox_headers )
headers2 = {
'User-Agent': 'Mozilla/5.0',
    'Authorization': 'token 4f9076590e87a4676d53698e3d240f34ac5cd24b ',
    'Content-Type': 'application/json',
    'method': 'GET', 'Accept': 'application/json'}

#默认主页
def index(request):
    return render(request,'index.html')

class parsePageInfo(threading.Thread):
    def __init__(self, threadName, dataQueue):
        super(parsePageInfo, self).__init__()
        # 线程名
        self.threadName = threadName
        # 数据队列
        self.dataQueue = dataQueue
        self.__mutex = threading.Lock()  # 初始化互斥量
        self.__cond = threading.Condition(self.__mutex)  # 初始化条件变量
        # 保存解析后数据的文件名
    def run(self):
        while not PARSE_EXIT:
            if self.__cond.acquire():
                while (self.dataQueue.empty()):
                    self.__cond.wait()
                try:
                    html = self.dataQueue.get(False)
                    index = html['index']
                    print(str(index) + "---" + html['items'][index]['full_name'])
                    self.fetchData(html['items'][index]['full_name'])

                except BaseException as e:
                    pass
                finally:
                    self.__cond.notify()
                    self.__cond.release()
    def fetchData(self,repo):
        initial.initial(repo)


class getPageInfo(threading.Thread):
    def __init__(self, threadName, pageQueue , dataQueue,search_url):
        # threading.Thread.__init__(self)
        # 调用父类初始化方法
        super(getPageInfo, self).__init__()
        # 线程名
        self.threadName = threadName
        # 页码队列
        self.pageQueue = pageQueue
        # 数据队列
        self.dataQueue = dataQueue
        self.search_url = search_url
        self.__mutex = threading.Lock()  # 初始化互斥量
        self.__cond = threading.Condition(self.__mutex)  # 初始化条件变量
    def run(self):
        try:
            while not CRAWL_EXIT:
                if self.__cond.acquire():
                    while(self.pageQueue.empty()):
                        self.__cond.wait()
                    page = self.pageQueue.get(False)
                    url = self.search_url+"&page=" + str(page)
                    html = requests.get(url, headers=headers2).text
                    info = json.loads(html)
                    #把爬下来的数据放到数据队列中
                    for i in range(0,len(info['items'])):
                        print(str(page)+'---'+str(i)+'---'+info['items'][i]['full_name'])
                        initial.initial(info['items'][i]['full_name'])
                        time.sleep(1)
                    self.__cond.notify()
                    self.__cond.release()
                '''
                if (info and len(info['items'])>0):
                    for i in range(0, len(info['items'])):
                        info['index'] = i
                        self.dataQueue.put(info)
                '''
        except BaseException as e:
            pass

CRAWL_EXIT = False
PARSE_EXIT = False
#ajax传递页面
def search_repo(request):
    #查找关键字所提供的q下所有repo
    q = request.POST['repo']
    '''
    url = 'https://api.github.com/repos/Microsoft/vscode'
    html = requests.get(url, headers=headers).text  # follow
    data = json.loads(html)
    downloadIssues.downloadIssuesInfo(data)
    sys.exit()
    '''

    search_url = 'https://api.github.com/search/repositories?q=stars:%3E10000&sort=stars&per_page=100'
    search_Response = requests.get(search_url, headers=headers2)  # follow
    headData = str(search_Response.headers)  # 获取头部信息
    listLink_last_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\"last)', headData)  # 获取最后一页
    # 获取最后一页页码
    if (listLink_last_url and listLink_last_url[0] != ''):
        last_page = re.findall(r'&page=([^&#]*)', listLink_last_url[0])
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
    #crawlList = ["get_tr1", "get_tr2", "get_tr3", "get_tr4"]
    crawlList = ["get_tr1"]
    # 存储三个采集线程的列表集合
    threadcrawl = []
    for threadName in crawlList:
        thread = getPageInfo(threadName, pageQueue, dataQueue,search_url)
        thread.start()
        threadcrawl.append(thread)

    # 设置三个解析线程的名字
    parseList = ["parse_tr1", "parse_tr2", "parse_tr3"]
    # 存储三个解析线程
    threadparse = []
    for threadName in parseList:
        thread = parsePageInfo(threadName, dataQueue)
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
        print("2")
    '''
    # 空白输入
    repo = request.POST['repo'];
    if ( repo == ''):
        return HttpResponse(-1);
    # 查找开始时间戳
    file_timeStampStart = './public/data/' + repo + '/timeStampStart'; # 查找有无下载开始的时间戳
    #如果输入的仓库还没有下载则开始下载
    if(os.path.isfile(file_timeStampStart)==False):
        start = '2008-01-01';
        end = datetime.datetime.now().strftime('%Y-%m-%d');
        ret = fetchData(repo, start, end);
        if(ret==1): #不存在该仓库
            return HttpResponse(-2);
    else:
        try:
            fs = open(file_timeStampStart,'r');
        except IOError  as reason:
            print('出错啦！' + str(reason))
        finally:
            if fs in locals():
                fs.close()
   
    '''
    return HttpResponse("上传成功!");

