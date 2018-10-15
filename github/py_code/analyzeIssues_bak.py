import json
import re
import os
import time
import datetime
import calendar


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

    for file in files:
        with open(cDir + file,'r') as f:
            data = json.loads(f.read())

            for item in data:
                user = item["user"]["id"]
                if(user not in allReporter):
                    allReporter[user] = 0
                allReporter[user] += 1
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
    averageDealTime = allDays / closedCount
    print(folder + " average:",averageDealTime)
    print(folder + " dealdRate:", closedCount/allCount )

    # 统计所有开发者的id
    with open("public/"+folder+"/allUsersId.json",'r') as f:
        allUsersId = json.loads(f.read())

    insideReporterCount = 0
    allReporterCount = 0
    insideReports = 0

    for item in allReporter:
        if item in allUsersId:
            insideReporterCount += 1
        allReporterCount += 1
    if(allReporterCount):
        print("inside/all:", insideReporterCount / allReporterCount)


repos = ["d3/d3","airbnb/javascript","nlohmann/json"]

'''
for item in repos:
    dividePrsansIssues(item)
'''
for item in repos:
    analyzeIssues(item)

    # 区分内部报告者和外部报告
