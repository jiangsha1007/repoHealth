# -*- coding: utf-8 -*-
import json
import re
import github
import log
import urllib2
import requests
import logging
from common_header import headers
# 使用了线程库
import threading
from threading import Thread,Lock
# 队列
import queue
headers = {
    'User-Agent':'Mozilla/5.0',
    'Authorization': 'token 4f9076590e87a4676d53698e3d240f34ac5cd24b',
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
        if (html):
            for i in range(0,len(html)):  # 遍历获取member信息
                v = html[i]
                org_members_id = v['id']
                org_members_name = v['login']
                org_members_avatar_url = v['avatar_url']
                org_member_type_str = v['type']
                if (org_member_type_str == 'Organization'):
                    org_member_type = 1
                else:
                    org_member_type = 0
                try:  # 判断用户表里是否已经存在,不存在则加到用户表
                    user_is = github.models.User_Org_Info.objects.filter(user_id=org_members_id)  # 判断用户或组织是否存在
                    if (len(user_is) < 1):
                        user_member_new = github.models.User_Org_Info.objects.create(user_id=org_members_id,
                                                                                     user_name=org_members_name,
                                                                                     avatar_url=org_members_avatar_url,
                                                                                     user_type=org_member_type)
                        user_member_new.save()
                except BaseException as e:
                    pass

                try:  # 判断组织关系表里是否存在，不存在则加到组织关系表
                    user_member_is = github.models.Org_Members_Info.objects.filter(org=self.data['id'],
                                                                                   member_id=org_members_id)  # 判断用户或组织是否存在
                    if (len(user_member_is) < 1):
                        _org = github.models.User_Org_Info.objects.filter(user_id=self.data['id'])
                        user_member_new = github.models.Org_Members_Info.objects.create(org=_org[0],
                                                                                        member_id=org_members_id)
                        user_member_new.save()
                except BaseException as e:
                    # set_log(e)
                    print('--org')
                    print(e)


#获取org_member页面
class getPageInfo(threading.Thread):
    def __init__(self, threadName, pageQueue , dataQueue, org_member_url):
        # threading.Thread.__init__(self)
        # 调用父类初始化方法
        super(getPageInfo, self).__init__()
        # 线程名
        self.threadName = threadName
        # 页码队列
        self.pageQueue = pageQueue
        # 数据队列
        self.dataQueue = dataQueue
        self.org_member_url = org_member_url
    def run(self):

            while not CRAWL_EXIT:
                try:
                    page = self.pageQueue.get(False)

                    org_member_url = self.org_member_url+"&page=" + str(page)
                    # 循环获取headers
                    header_index = 0
                    r = requests.get(org_member_url, headers=headers[header_index])
                    while (r.status_code == 301):
                        header_index = header_index + 1
                        header_index = header_index % 5
                        r = requests.get(org_member_url, headers=headers[header_index])
                    html = r.text
                    info = json.loads(html)
                    #把爬下来的数据放到数据队列中
                    if (info):
                        self.dataQueue.put(info)
                except BaseException as e:
                    pass

CRAWL_EXIT = False
PARSE_EXIT = False

def getUserInfo(data):
    try:
        owner_id = data['id']
        user_name = data['login']
        if(data.has_key('name')):
            user_fullname = data['name']
        else:
            user_fullname = ''
        avatar_url = data['avatar_url']
        user_url = data['url']
        user_html = requests.get(user_url, headers=headers).text
        user_info = json.loads(user_html)
        #follows的信息
        if(user_info):
            follows_count = user_info['followers']
            repos_count = user_info['public_repos']
            user_blog_url = user_info['blog']
            user_email_url = user_info['email']
            user_create_time = user_info['created_at']
            user_update_time = user_info['updated_at']
            user_type = user_info['type']
        else:
            follows_count = 0
            repos_count = 0
            user_email_url = ''
            user_create_time = ''
            user_update_time = ''
            user_type = 'User'
        try:
            user = github.models.User_Org_Info.objects.filter(user_id = owner_id) #判断用户或组织是否存在
            if(user and len(user)>0):
                user[0].user_name = user_name
                user[0].user_fullname = user_fullname
                user[0].avatar_url = avatar_url
                user[0].follow_count = follows_count
                user[0].repos_count = repos_count
                user[0].blog_url = user_blog_url
                user[0].email_url = user_email_url
                user[0].user_type = user_type
                user[0].user_create_time = user_create_time
                user[0].user_update_time = user_update_time
                user[0].save()
            else:
                try:
                    user_new = github.models.User_Org_Info.objects.create(user_id=owner_id,
                                                                      user_name=user_name,
                                                                      user_fullname=user_fullname,
                                                                      avatar_url=avatar_url,
                                                                      follows_count=follows_count,
                                                                      repos_count=repos_count,
                                                                      blog_url=user_blog_url,
                                                                      email_url=user_email_url,
                                                                      user_type=user_type,
                                                                      user_create_time=user_create_time,
                                                                      user_update_time=user_update_time)
                    user_new.save()
                except:
                    pass
        except BaseException as e:
            set_log(e)



        # 如果是组织，获取组织下的members数量和对应的member
        if(user_type=='Organization'):
            flag = True
            members_count = 0
            org_member_url = "https://api.github.com/orgs/" + user_name + "/members?per_page=100" #member地址
            org_member_Response = requests.get(org_member_url, headers=headers)  # follow
            headData = str(org_member_Response.headers)  # 获取头部信息
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
            crawlList = ["get_tr1", "get_tr2", "get_tr3"]
            # 存储三个采集线程的列表集合
            global CRAWL_EXIT
            CRAWL_EXIT = False
            global PARSE_EXIT
            PARSE_EXIT = False
            threadcrawl = []
            for threadName in crawlList:
                thread = getPageInfo(threadName, pageQueue, dataQueue, org_member_url)
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
            #global CRAWL_EXIT
            CRAWL_EXIT = True

            for thread in threadcrawl:
                thread.join()

            while not dataQueue.empty():
                pass

            #global PARSE_EXIT
            PARSE_EXIT = True

            for thread in threadparse:
                thread.join()
            members_count = github.models.Org_Members_Info.objects.filter(org_id=owner_id).count()
            github.models.User_Org_Info.objects.filter(user_id=owner_id).update(org_member_count=members_count)
    except BaseException as e:
        set_log(e)

def getRepoInfo(data,url):
    repo_name = data['name']
    repo_fullname = data['full_name']
    repo_id = data['id']
    repo_description = ''#data['description']
    fork_count = data['forks_count']
    star_count = data['stargazers_count']
    subscribe_count = data['subscribers_count']
    repo_created_time = data['created_at']
    repo_update_time = data['updated_at']
    repo_size = data['size']
    owner_type =data['owner']['type']
    repo_owner = github.models.User_Org_Info.objects.filter(user_id = data['owner']['id'])
    if(len(repo_owner)<1):
        repo_owner = github.models.User_Org_Info.objects.filter(user_id=1)
    # 获取language数据
    languages_url = data['languages_url']
    languages_info = requests.get(languages_url, headers=headers).text
    languages_data = json.loads(languages_info)
    languages = {}
    if isinstance(languages_data, dict):  # 判断是否是字典类型isinstance 返回True false
        for key in languages_data:
            languages[key] = languages_data[key]
    languages = json.dumps(languages, ensure_ascii=False, encoding='UTF-8')
    try:
        repo_is = github.models.Repo_Base_Info.objects.filter(repo_id = repo_id)
        if(repo_is and len(repo_is)>0):

            repo_is[0].language =languages
            repo_is[0].fork_count = fork_count
            repo_is[0].star_count = star_count
            repo_is[0].subscribe_count = subscribe_count
            repo_is[0].repo_created_time = repo_created_time
            repo_is[0].repo_update_time = repo_update_time
            repo_is[0].repo_size = repo_size
            repo_is[0].owner_type = owner_type
            repo_is[0].repo_owner = repo_owner[0]
            repo_is[0].save()
        else:
            repoinfo = github.models.Repo_Base_Info.objects.create(repo_name=repo_name,
                                                                   repo_full_name=repo_fullname,
                                                                   repo_id=repo_id, language=languages,
                                                                   repo_description=repo_description,
                                                                   fork_count=fork_count,
                                                                   star_count=star_count,
                                                                   subscribe_count=subscribe_count,
                                                                   repo_created_time=repo_created_time,
                                                                   repo_update_time=repo_update_time,
                                                                   repo_size=repo_size,
                                                                   owner_type=owner_type,
                                                                   repo_owner=repo_owner[0])
            repoinfo.save()
    except BaseException as e:
        set_log(e)
def downloadBaseInfo(data,url):
    getUserInfo(data['owner'])   #获取用户信息
    getRepoInfo(data,url)   #获取repo信息

def set_log(e):
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s"
    logging.basicConfig(format=LOG_FORMAT)
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    fh = logging.FileHandler('error.log')
    fh.setFormatter(LOG_FORMAT)
    logger.addHandler(fh)
    logger.error(e)