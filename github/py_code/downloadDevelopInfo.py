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
headers = {
    'User-Agent':'Mozilla/5.0',
    'Authorization': 'token 8f6085fc4cf4b501a7ccad1a3aadc3f98f51384a',
    'Content-Type':'application/json',
    'method': 'GET', 'Accept': 'application/json'}  # 构建请求 request = Request( url, headers=firefox_headers )
class getDeveloperInfo(threading.Thread):
    def __init__(self, threadName, pageQueue, data):
        # threading.Thread.__init__(self)
        # 调用父类初始化方法
        super(getDeveloperInfo, self).__init__()
        # 线程名
        self.threadName = threadName
        # 页码队列
        self.pageQueue = pageQueue
        self.data = data
    def run(self):
        try:
            repo_id = self.data['id']
            global commit_total_count
            #repo_owner = github.models.Repo_Base_Info.objects.get(repo_id=repo_id)  #获取repo_id
            #先查询contributor，找到所有contributor，然后遍历，获取一些数据，然后在通过commit?auth= 查询具体每次commit
            #contributor_url = self.data['contributors_url']+"?anon=1"
            #flag = True
            while not CRAWL_EXIT:
                page = self.pageQueue.get(False)
                contributor_url = self.data['contributors_url'] + "?anon=1&per_page=100&page=" + str(page)
                contributor_html = requests.get(contributor_url, headers=headers).text
                contributor_info = json.loads(contributor_html)
                if (contributor_info):
                    for i in range(len(contributor_info)):  # 遍历获取contributor信息
                        #time.sleep(1)
                        v = contributor_info[i]
                        contributor_contributions = v['contributions']
                        #如果是用户
                        if(contributor_info[i].has_key('id')):
                            contributor_id = v['id']
                            contributor_name = v['login']
                            contributor_avatar_url = v['avatar_url']
                            contributor_type = v['type']
                            try:
                                contributor_user = github.models.User_Org_Info.objects.get(user_id=contributor_id)  # 获取repo_id
                            except github.models.User_Org_Info.DoesNotExist:
                                user_new = github.models.User_Org_Info.objects.create(user_id=contributor_id,
                                                                                     user_name=contributor_name,
                                                                                     avatar_url=contributor_avatar_url,
                                                                                     user_type=contributor_type)
                                user_new.save()
                            contributor_commit_user = contributor_name
                        #如果是匿名
                        else:
                            contributor_email = v['email']
                            contributor_fullname = v['name']
                            contributor_type = v['type']
                            try:
                                contributor_user = github.models.User_Org_Info.objects.get(email_url=contributor_email)  # 获取repo_id
                                contributor_id = contributor_user.user_id
                            except github.models.User_Org_Info.DoesNotExist:
                                random_id = ''.join(str(random.choice(range(10))) for _ in range(5))   #获取随机数
                                t = time.time()                                                         #获取时间戳
                                time_stamp =str((int(round(t * 1000))))
                                time_stamp = time_stamp[-9:]
                                contributor_id = '9'+random_id+time_stamp
                                user_new = github.models.User_Org_Info.objects.create(user_id = contributor_id,
                                                                                    email_url=contributor_email,
                                                                                      user_fullname=contributor_fullname,
                                                                                     user_type=contributor_type)
                                user_new.save()
                            contributor_commit_user = contributor_email
                        #先查找表里是否存在，如存在且commit数量相同，则跳过
                        contributor_user = github.models.User_Org_Info.objects.filter(user_id=contributor_id)
                        contributor_repo = github.models.Repo_Base_Info.objects.filter(repo_id=repo_id)
                        developer = github.models.Repo_Developer_info.objects.filter(
                            Q(repo=contributor_repo) & Q(user=contributor_user))  # 判断用户或组织是否存在
                        #if(developer and developer[0].user_commit_count == contributor_contributions):
                        #    continue

                        #读取commit的第一页和最后一页，主要读取第一次commit时间和最后一次commit时间
                        commit_user_url_first = self.data["commits_url"][0:-6] + "?author=" + contributor_commit_user
                        commit_user_req = urllib2.Request(commit_user_url_first, headers=headers)
                        commit_user_res = urllib2.urlopen(commit_user_req)
                        commit_user_html = commit_user_res.read()
                        commit_user_info = json.loads(commit_user_html)
                        if(commit_user_info and len(commit_user_info)>0 ):
                            if(commit_user_info[0].has_key('commit')):
                                user_last_update_time = commit_user_info[0]['commit']['author']['date']

                        #if (developer):
                        #    user_creat_time = developer[0].user_creat_time
                        #else:
                        #计算commit页数，按照每页30计算
                            commit_page = contributor_contributions/30
                            commit_page_yu = contributor_contributions%30
                            if(commit_page_yu!=0):
                                commit_page = commit_page+1
                            if(commit_page==0):#如果只有一页
                                if (commit_user_info[len(commit_user_info)-1].has_key('commit')):
                                    user_creat_time = commit_user_info[len(commit_user_info)-1]['commit']['author']['date']
                                    lock.acquire()
                                    commit_total_count += len(commit_user_info)
                                    lock.release()
                            else:
                                commit_user_url_last = self.data["commits_url"][0:-6] + "?author=" + contributor_commit_user + "&page=" + str(commit_page)
                                commit_user_last_req = urllib2.Request(commit_user_url_last, headers=headers)
                                commit_user_last_res = urllib2.urlopen(commit_user_last_req)
                                commit_user_last_html = commit_user_last_res.read()
                                commit_user_last_info = json.loads(commit_user_last_html)
                                if (commit_user_last_info and len(commit_user_last_info) > 0):
                                    if (commit_user_last_info[len(commit_user_last_info) - 1].has_key('commit')):
                                        user_creat_time = commit_user_last_info[len(commit_user_last_info) - 1]['commit']['author']['date']
                                        lock.acquire()
                                        commit_total_count +=(commit_page-1)*30 + len(commit_user_last_info)
                                        lock.release()
                        #插入表格中
                        try:
                            developer = github.models.Repo_Developer_info.objects.get( Q(repo = contributor_repo) & Q(user=contributor_user)) # 判断用户或组织是否存在
                            developer.user_creat_time = user_creat_time
                            developer.user_last_update_time = user_last_update_time
                            developer.user_commit_count = contributor_contributions
                            developer.save()

                        except github.models.Repo_Developer_info.DoesNotExist:
                            developer_new = github.models.Repo_Developer_info.objects.create(repo=contributor_repo[0],
                                                                                             user=contributor_user[0],
                                                                                             user_creat_time=user_creat_time,
                                                                                             user_last_update_time=user_last_update_time,
                                                                                             user_commit_count=contributor_contributions)
                            developer_new.save()

            #循环结束
            #线程1获取commit数量
            if(threading.current_thread().getName()=='tr2'):
                issue_url = self.data["issues_url"][0:-9]+"?filter=all"
        except BaseException as e:
            log.set_log(e)
def getDeveloper_Contribute(data):
    try:
        # 根据/stats/contributors 获取前99comiit贡献者
        contributor_repo = github.models.Repo_Base_Info.objects.filter(repo_id=data['id'])
        statistic_contributors_url = data['url'] + "/stats/contributors"
        statistic_contributors_html = requests.get(statistic_contributors_url, headers=headers).text
        statistic_contributors_info = json.loads(statistic_contributors_html)
        if (statistic_contributors_info):
            for i in range(len(statistic_contributors_info)):  # 遍历获取statistic_contributors信息
                statistic_contributors_user_id = statistic_contributors_info[i]['author']['id']
                contributor_user = github.models.User_Org_Info.objects.filter(user_id=statistic_contributors_user_id)

                add_perweek = {}
                del_perweek = {}
                commit_perweek = {}
                statistic_contributors_perweek = statistic_contributors_info[i]['weeks']
                for j in range(len(statistic_contributors_perweek)):  # 遍历获取statistic_contributors_info['weeks']信息
                    if isinstance(statistic_contributors_perweek[j], dict):  # 判断是否是字典类型isinstance 返回True false
                        key = statistic_contributors_perweek[j]['w']
                        add_perweek[key] = statistic_contributors_perweek[j]['a']
                        del_perweek[key] = statistic_contributors_perweek[j]['d']
                        commit_perweek[key] = statistic_contributors_perweek[j]['c']
                add_perweek = json.dumps(add_perweek, ensure_ascii=False, encoding='UTF-8')
                del_perweek = json.dumps(del_perweek, ensure_ascii=False, encoding='UTF-8')
                commit_perweek = json.dumps(commit_perweek, ensure_ascii=False, encoding='UTF-8')
                github.models.Repo_Developer_info.objects.filter(Q(repo=contributor_repo) & Q(user=contributor_user)) \
                    .update(user_commit_count_perweek=commit_perweek, user_add_count_perweek=add_perweek,
                            user_del_count_perweek=del_perweek)  # 判断用户或组织是否存在
    except BaseException as e:
        log.set_log(e)

CRAWL_EXIT = False
commit_total_count = 0;
lock = Lock()
def downloadDevelopInfo(data):
    #通过多线程和队列加速爬取速度
    #第一步，获取宗总的页码数量
    contributors_url = data['contributors_url'] + "?anon=1&per_page=100"
    contributors_Response = requests.get(contributors_url, headers=headers)  # follow
    headData = str(contributors_Response.headers)  # 获取头部信息
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
    # 第三步，把页数放到队列里，先进先出
    for i in range(1, last_page_int+1):
        pageQueue.put(i)
    # 三个采集线程的名字
    crawlList = ["tr1", "tr2", "tr3"]
    # 存储三个采集线程的列表集合
    threadcrawl = []
    for threadName in crawlList:
        thread = getDeveloperInfo(threadName, pageQueue, data)
        thread.start()
        threadcrawl.append(thread)
    # 等待pageQueue队列为空，也就是等待之前的操作执行完毕
    while not pageQueue.empty():
        pass
    # 如果pageQueue为空，采集线程退出循环
    global CRAWL_EXIT
    CRAWL_EXIT = True

    for thread in threadcrawl:
        thread.join()
    #new_thread = threading.Thread(target = getDeveloperInfo, args=(data,))
    #new_thread.start()
    getDeveloper_Contribute(data)
    #getDeveloperInfo(data)   #获取用户信息
    #getDevelopInfo(data)   #获取repo信息
