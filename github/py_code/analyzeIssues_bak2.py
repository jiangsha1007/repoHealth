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


def getDuration(start,end):

    start = time.strptime(start[0:10],"%Y-%m-%d")
    end = time.strptime(end[0:10],"%Y-%m-%d")

    start = datetime.datetime(start.tm_year,start.tm_mon,start.tm_mday)
    end = datetime.datetime(end.tm_year,end.tm_mon,end.tm_mday)
    duration = (end - start).days

    return duration


def dividePrsansIssues(repo):
    repos = repo.split(sep="/")
    organ = repos[0]
    folder = repos[1]

    cDir = "public/" + folder + "/" + "issues/"
    files = os.listdir(cDir)
    issuesDir = "public/" + folder + "/" + "dealdIssues/"
    prsDir = "public/" + folder +"/pr/"

    isExists = os.path.exists(issuesDir)
    if not isExists:
        os.makedirs(issuesDir)

    isExists = os.path.exists(prsDir)
    if not isExists:
        os.makedirs(prsDir)

    print(files)
    count = 1
    for file in files:
        with open(cDir + file,'r') as f:
            data = json.loads(f.read())
            newIssues = []
            newPRs = []

            for item in data:
                newItem = item

                if ( "pull_request" not in item):

                    newIssues.append(newItem)
                else:
                    newPRs.append(newItem)

        with open(issuesDir + "issues-" + str(count) + ".json",'w') as f:
            json.dump(newIssues,f)
        with open(prsDir + "pull_request" + str(count) + ".json",'w') as f:
            json.dump(newPRs,f)
        count += 1

def analyzeIssues(repo):
    repos = repo.split(sep="/")
    organ = repos[0]
    folder = repos[1]

    cDir = "public/" + folder + "/" + "dealdIssues/"
    files = os.listdir(cDir)

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
    with open("public/"+folder+"/allReporterId.json",'w') as f:
        json.dump(allReporterlist,f)
    averageDealTime = allDays / closedCount
    print(folder + " average:",averageDealTime)
    print(folder + " dealdRate:", closedCount/allCount )

    # 统计按年份计算内部开发者比例的变化
    currentinusercount=[0 for x in range(0,11)]
    currentusercount=[0 for x in range(0,11)]
    currentrate=[0 for x in range(0,11)]
    totalinuser=0
    totaluser=0

    strMonths = []
    for i in range(1,10):
        strMonths.append("0" + str(i))
    for i in range(10,13):
        strMonths.append(str(i))

    dir = "public/JSON/dealdIssues/"
    for year in range(2008,2019):
        for month in range(0,12):
            with open(dir+str(year)+"-"+strMonths[month]+".json","r")as f:
                data=json.loads(f.read())
                with open("public/" + folder + "/insideReporterId.json",'r') as f:
                    insideUsersId = json.loads(f.read())
                    for item in data:
                        if item in insideUsersId:
                            currentinusercount[year-2008]+=1
                        currentusercount[year-2008]+=1
        totalinuser=totalinuser+currentinusercount[year-2008]
        totaluser=totaluser+currentusercount[year-2008]
        if (totaluser):
            currentrate[year-2008]=totalinuser/totaluser
    list = [("2008", currentrate[0]), ("2009", currentrate[1]), ("2010", currentrate[2]),
            ("2011", currentrate[3]), ("2012", currentrate[4]),("2013", currentrate[5]),
            ("2014", currentrate[6]),("2015", currentrate[7]),("2016", currentrate[8]),
            ("2017", currentrate[9]),("2018", currentrate[10])]
    x, y= pyecharts.base.Base.cast(list)
    line = Line("LINE CHART", "inside user part")
    line.add("outside users", x, y)
    line.render()


    # 统计所有开发者的id
    #计算内部开发着比例
    with open("public/"+folder+"/allUsersId.json",'r') as f:
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

    # 计算内部和外部开发者的平均解决时间和解决率
####################################################
    outsideallDays = 0
    outsideclosedCount = 0
    outsideallCount = 0

    insideallDays = 0
    insideclosedCount = 0
    insideallCount = 0


    with open("public/"+folder+"/insideReporterId.json",'w') as f:
        json.dump(insideReporterlist,f)

    with open("public/"+folder+"/insideReporterId.json",'r') as f:
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
        insideaverageDealTime = insideallDays / insideclosedCount
        outsideaverageDealTime = outsideallDays / outsideclosedCount

    # 以issue处理天数统计用户数量，折线图，生成render html文件
        inlist=[("1day",inoneday),("5days",infiveday),("20days",intwentyday),
                ("50days",infiftyday),("moredays",inother)]
        outlist = [("1day", outoneday), ("5days", outfiveday), ("20days", outtwentyday),
                  ("50days", outfiftyday), ("moredays", outother)]
        x,y1=pyecharts.base.Base.cast(inlist)
        x,y2=pyecharts.base.Base.cast(outlist)


        line=Line("LINE CHART","In and Out Users ISSUE Processing TIME")
        line.add("inside users",x,y1)
        line.add("outside users",x,y2)
        line.render()

        print(folder + " insideaverage:", insideaverageDealTime)
        print(folder + " insidedealdRate:", insideclosedCount / insideallCount)

        print(folder + " outsideaverage:", outsideaverageDealTime)
        print(folder + " outsidedealdRate:", outsideclosedCount / outsideallCount)

# repos = ["d3/d3","airbnb/javascript","nlohmann/json"]
#
# '''
# for item in repos:
#     dividePrsansIssues(item)
# '''
# for item in repos:
repo="nlohmann/json"
analyzeIssues(repo)

    # 区分内部报告者和外部报告
