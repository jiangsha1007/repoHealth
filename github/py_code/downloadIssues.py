# -*- coding: utf-8 -*-
import json
from django.db.models import Q
import re
import github
import log
from common_header import headers
from urllib3.exceptions import ReadTimeoutError, ConnectTimeoutError
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
headers2 = {
    'User-Agent':'Mozilla/5.0',
    'Authorization': 'token 4f9076590e87a4676d53698e3d240f34ac5cd24b',
    'Content-Type':'application/json',
    'method': 'GET', 'Accept': 'application/json'}
class parsePageInfo(threading.Thread):
    def __init__(self, threadName, dataQueue, data):
        super(parsePageInfo, self).__init__()
        # 线程名
        self.threadName = threadName
        # 数据队列
        self.dataQueue = dataQueue
        # 保存解析后数据的文件名
        self.data = data
        self.__mutex = threading.Lock()  # 初始化互斥量
        self.__cond = threading.Condition(self.__mutex)  # 初始化条件变量
    def run(self):

        while not PARSE_EXIT:
            if self.__cond.acquire():
                while (self.dataQueue.empty()):
                    self.__cond.wait()
                try:
                    html = self.dataQueue.get(False)
                    self.parse(html)
                except:
                    pass
                finally:
                    self.__cond.notify()
                    self.__cond.release()
    def parse(self, html):
        for i in range(len(html)):  # 遍历获取contributor信息
            try:
                v = html[i]
                #github里把pull_request看作一次issue,在这里需要排除
                if(v.has_key('pull_request')):
                    continue
                issue_id = v['id']
                issue_number = v['number']
                issue_state = v['state']
                if(issue_state=='open'):
                    issue_state = 0
                elif(issue_state=='closed'):
                    issue_state = 1
                else:
                    issue_state = 2

                issue_create_time = v['created_at']
                issue_update_time = v['updated_at']
                issue_close_time = v['closed_at']
                issue_comment_count = v['comments']
                issue_user_type = v['author_association']
                issue_user_id = v['user']['id']
                user = github.models.User_Org_Info.objects.filter(user_id = issue_user_id)
                if(len(user)<1):
                    downloadBaseInfo.getUserInfo(v['user'])
                user = github.models.User_Org_Info.objects.filter(user_id=issue_user_id)
                repo = github.models.Repo_Base_Info.objects.filter(repo_id = self.data['id'])
                try:
                    issues = github.models.Repo_Issue_info.objects.filter(
                        Q(issue_id=issue_id) & Q(issue_number=issue_number))  # 判断用户或组织是否存在
                    if(issues and len(issues)>0):
                        issues[0].issue_state = issue_state
                        issues[0].issue_update_time = issue_update_time
                        issues[0].issue_close_time = issue_close_time
                        issues[0].issue_comment_count = issue_comment_count
                        issues[0].save()
                    else:
                        issues_new = github.models.Repo_Issue_info.objects.create(repo=repo[0],
                                                                                  user=user[0],
                                                                                  issue_id=issue_id,
                                                                                  issue_number=issue_number,
                                                                                  issue_create_time=issue_create_time,
                                                                                  issue_update_time=issue_update_time,
                                                                                  issue_close_time=issue_close_time,
                                                                                  issue_comment_count=issue_comment_count,
                                                                                  issue_user_type=issue_user_type,
                                                                                  issue_state=issue_state
                                                                                  )
                        issues_new.save()
                except BaseException as ex:
                    pass

            except BaseException as e:
                log.set_log(e)






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
        self.__mutex = threading.Lock()  # 初始化互斥量
        self.__cond = threading.Condition(self.__mutex)  # 初始化条件变量
    def run(self):
        while not CRAWL_EXIT:
            if self.__cond.acquire():
                while (self.pageQueue.empty()):
                    self.__cond.wait()
                try:
                    page = self.pageQueue.get(False)
                    issues_url = self.data["issues_url"][0:-9]+"?per_page=100&state=all"+"&page=" + str(page)
                    # 循环获取headers
                    header_index = 0
                    print(issues_url)
                    try:
                        r = requests.get(issues_url, headers=headers[0])
                        issue_html = r.text
                        issue_info = json.loads(issue_html)
                        # 把爬下来的数据放到数据队列中
                        if (issue_info):
                            self.dataQueue.put(issue_info)
                        if(r.status_code == 301):
                            while (r.status_code == 301):
                                header_index = header_index + 1
                                header_index = header_index % 5
                                r = requests.get(issues_url, headers=headers[header_index])
                            issue_html = r.text
                            issue_info = json.loads(issue_html)
                            # 把爬下来的数据放到数据队列中
                            if (issue_info):
                                self.dataQueue.put(issue_info)
                    except ReadTimeoutError:
                        print("ReadTimeoutError")
                    except ConnectTimeoutError:
                        print("ConnectTimeoutError")
                    except BaseException as ex:
                        print(ex)

                except BaseException as e:
                    pass
                    continue
                finally:
                    self.__cond.notify()
                    self.__cond.release()

CRAWL_EXIT = False
PARSE_EXIT = False
def downloadIssuesInfo(data):
    # 通过多线程和队列加速爬取速度,分为采集线程和数据处理线程
    # 首先是采集线程
    # 第一步，获取总的页码数量
    if(data.has_key('issues_url')):
        issue_url = data["issues_url"][0:-9]+"?per_page=100&state=all"
        issue_Response = requests.get(issue_url, headers=headers2)  # follow
        headData = str(issue_Response.headers)  # 获取头部信息
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
        global CRAWL_EXIT
        CRAWL_EXIT = False
        global PARSE_EXIT
        PARSE_EXIT = False
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

        CRAWL_EXIT = True

        for thread in threadcrawl:
            thread.join()

        while not dataQueue.empty():
            pass

        PARSE_EXIT = True

        for thread in threadparse:
            thread.join()