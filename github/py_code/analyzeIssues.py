# -*- coding: utf-8 -*
import json
import re
import os
import time
import datetime
import calendar

from pyecharts import Bar
from pyecharts import Line
from pyecharts import Pie

import pyecharts

#画内部开发者比例年份变化折线图
def plotinsideuserpart(cDir):
    with open(cDir +"insideuserpart.json",'r') as f:
        list = json.loads(f.read())
    print(list)
    (x, y)= pyecharts.base.Base.cast(list)
    print(x,y)
    line = Line("LINE CHART", "inside user proportion")
    line.add("inside monthly", x, y)
    line.render(cDir + "insideUserRate.html")

#画内部和外部开发者issue持续时间统计图
def plotinoutissuetime(cDir):
    with open(cDir +"inissueprocesstime.json",'r') as f:
        inli = json.loads(f.read())
    with open(cDir + "outissueprocesstime.json",'r') as f:
        outli = json.loads(f.read())

    (x,y1)=pyecharts.base.Base.cast(inli)
    (x,y2)=pyecharts.base.Base.cast(outli)

    line=Line("LINE CHART","In and Out Users ISSUE processing TIME")
    line.add("inside users",x,y1)
    line.add("outside users",x,y2)
    line.render(cDir + "resolvingTime.html")
def draw(repo):
    cDir = "public/data/" + repo + "/issues/"
    plotinsideuserpart(cDir)
    plotinoutissuetime(cDir)

def getDuration(start,end):

    start = time.strptime(start[0:10],"%Y-%m-%d")
    end = time.strptime(end[0:10],"%Y-%m-%d")

    start = datetime.datetime(start.tm_year,start.tm_mon,start.tm_mday)
    end = datetime.datetime(end.tm_year,end.tm_mon,end.tm_mday)
    duration = (end - start).days

    return duration
def getAllUsersId(repo,endYear):
    # 在commit里查找所有开发者Id,存放在issue的文件夹中
    commitDir = "public/data/" + repo + "/commits/"
    allUserId = []
    allUsers = {}
    for year in range(2008,endYear+1):
        for month in range(1,13):
            file = commitDir + "%d-%02d-originalCommits.json" % (year,month)
            with open(file,'r') as f:
                data = json.loads(f.read())
                cnt = 0
                for item in data:
                    if not item["author"]:
                        continue
                    id = item["author"]["id"]
                    if id not in allUsers:
                        allUsers[id] = 1
                        allUserId.append(id)
    with open("public/data/" + repo + "/issues/allUsersId.json",'w') as f:
        json.dump(allUserId,f)

def analyzeIssues(repo,endYear):

    cDir = "public/data/" + repo + "/issues/"
    files = []
    for year in range(2008,endYear+1):
        for month in range(1,13):
            files.append("%d-%02d-issues.json" % (year,month))

    allDays = 0
    closedCount = 0
    allCount = 0

    allReporter = {}
    allReporterlist=[]
    for file in files:
        # print(file)
        with open(cDir + file,'r') as f:
            data = json.loads(f.read())

            for item in data:
                if not item["user"] :
                    continue
                user = item["user"]["id"]
                if(user not in allReporter):
                    allReporter[user] = 0

                allReporter[user] += 1
                allReporterlist.append(user)
                # 获取issues的解决时间

                if item["state"] == 'closed':
                    start = item["created_at"]
                    end = item["closed_at"]
                    duration = getDuration(start,end)
                    allDays += duration
                    closedCount += 1
                allCount += 1
    if(closedCount == 0):
        return
    with open(cDir + "allReporterId.json",'w') as f:
        json.dump(allReporterlist,f) #所有reporter的id

    averageDealTime = allDays / closedCount
    print("allCount:",allCount)
    print(repo + " average:",averageDealTime)
    print(repo + " dealdRate:", closedCount/allCount )

    # 统计所有开发者的id
    # 计算内部开发着比例
    getAllUsersId(repo,endYear)
    with open(cDir + "allUsersId.json",'r') as f:
        allUsersId = json.loads(f.read())

    insideReporterCount = 0
    allReporterCount = 0
    # insideReports = 0
    insideReporterlist=[]

    for item in allReporter:
        if item in allUsersId:
            insideReporterCount += 1
            insideReporterlist.append(item)
        allReporterCount += 1
    print(insideReporterCount)
    print(allReporterCount)
    if(allReporterCount):
        print("inside/all:", insideReporterCount / allReporterCount)

####################################################
    # 计算内部和外部开发者的平均解决时间和解决率
    outsideallDays = 0
    outsideclosedCount = 0
    outsideallCount = 0

    insideallDays = 0
    insideclosedCount = 0
    insideallCount = 0


    with open(cDir + "insideReporterId.json",'w') as f:
        json.dump(insideReporterlist,f)

    with open(cDir + "insideReporterId.json",'r') as f:
        insideUsersId = json.loads(f.read())
        inoneday=0
        infiveday=0
        intwentyday=0
        infiftyday=0
        inother=0

        outoneday=0
        outfiveday=0
        outtwentyday=0
        outfiftyday=0
        outother=0
        for file in files:
            with open(cDir + file, 'r') as f:
                data = json.loads(f.read())
                for item in data:
                    user = item["user"]["id"]
        #计算内部开发者的平均解决时间和解决率
                    if user in insideUsersId:
                        # print("yes")
                        if item["state"] == 'closed':
                            start = item["created_at"]
                            end = item["closed_at"]
                            duration = getDuration(start, end)
                            #按解决所用天数统计
                            if duration<1:
                                inoneday+=1
                            elif duration<5:
                                infiveday+=1
                            elif duration<20:
                                intwentyday+=1
                            elif duration<50:
                                infiftyday+=1
                            else:
                                inother+=1
                            insideallDays += duration
                            insideclosedCount += 1
                        insideallCount += 1
         #计算外部开发者的issue平均解决时间和解决率
                    else:
                        if item["state"] == 'closed':
                            start = item["created_at"]
                            end = item["closed_at"]
                            duration = getDuration(start, end)
                            if duration<1:
                                outoneday+=1
                            elif duration<5:
                                outfiveday+=1
                            elif duration<20:
                                outtwentyday+=1
                            elif duration<50:
                                outfiftyday+=1
                            else:
                                outother+=1
                            outsideallDays += duration
                            outsideclosedCount += 1
                        outsideallCount += 1
        if insideclosedCount == 0:
            insideaverageDealTime = 0
        else :
            insideaverageDealTime = insideallDays / insideclosedCount

        if outsideclosedCount == 0:
            outsideaverageDealTime = 0
        else:
            outsideaverageDealTime = outsideallDays / outsideclosedCount

    #以issue处理天数统计用户数量，折线图，生成render html文件
        inlist = [{"1day":inoneday, "5days":infiveday, "20days":intwentyday,
                  "50days":infiftyday,"moredays": inother}]
        outlist = [{"1day":outoneday,"5days":outfiveday,"20days":outtwentyday,
                    "50days":outfiftyday,"moredays":outother}]
        with open(cDir +"inissueprocesstime.json",'w') as f:
            json.dump(inlist,f)
        with open(cDir + "outissueprocesstime.json",'w') as f:
            json.dump(outlist,f)

        print(repo + " insideaverage:", insideaverageDealTime)
        #print(repo + " insidedealdRate:", insideclosedCount / insideallCount)
        print(repo + " outsideaverage:", outsideaverageDealTime)
        #print(repo + " outsidedealdRate:", outsideclosedCount / outsideallCount)

    # 分年份计算解决率
    l = endYear - 2008 + 1;
    currentinusercount=[0 for x in range(0,l)]
    currentusercount=[0 for x in range(0,l)]
    currentrate=[0 for x in range(0,l)]
    totalinuser=0
    totaluser=0

    for year in range(2008,endYear+1):
        for month in range(1,13):
            file = "%d-%02d-issues.json" % ( year,month)
            with open(cDir + file,"r")as f:
                data=json.loads(f.read())
                with open( cDir + "insideReporterId.json",'r') as f:
                    insideUsersId = json.loads(f.read())
                    for item in data:
                        id = item["user"]["id"]
                        if id in insideUsersId:
                            currentinusercount[year-2008]+=1
                        currentusercount[year-2008]+=1
        totalinuser=totalinuser+currentinusercount[year-2008]
        totaluser=totaluser+currentusercount[year-2008]
        #计算当前年份的内部开发者所占比例
        if (totaluser):
            currentrate[year-2008]=totalinuser/totaluser
    list = {}
    print("currentrate:")
    print(currentrate)
    for year in range(2008,endYear + 1):
        list[str(year)] = currentrate[year-2008]
    '''
    list = [{"2008":currentrate[0], "2009":currentrate[1],"2010":currentrate[2],
            "2011":currentrate[3],"2012":currentrate[4],"2013": currentrate[5],
            "2014": currentrate[6],"2015": currentrate[7],"2016":currentrate[8],
            "2017":currentrate[9],"2018":currentrate[10]}]
    '''
    with open(cDir +"insideuserpart.json",'w') as f:
        json.dump(list,f)
    draw(repo)

#
# repos = ["d3/d3","airbnb/javascript","nlohmann/json"]
#
# '''
# for item in repos:
#     dividePrsansIssues(item)
# '''
# for item in repos:
'''
repo="nlohmann/json"
#analyzeIssues(repo,2018)
draw(repo)
'''
    # 区分内部报告者和外部报告
