# -*- coding: utf-8 -*
# 寻找开发者平均贡献时间：第一次与最后一次代码贡献时间
# 生成一个duration.json 里面的参数为{用户email:{所有commits的时间}}
import json
import time
import datetime
import calendar

def findAllUsers(folder):
    cDir = "public/data/" + folder + "/commits/"
    allUsers = {}

    for year in range(2008,endYear):
        for month in range(1,13):
            date = str(year) + "-" + "%02d" % month
            file = date + "-commitsUser.json"

            with open(cDir + file, 'r') as f:
                data = json.loads(f.read())
                for user in data:
                    thisDate = data[user]
                    print(data[user])
                    if user not in allUsers:
                        allUsers[user] = []

                    allUsers[user] = allUsers[user] + data[user]

    with open(cDir + "allUsers.json",'w') as f:
        json.dump(allUsers,f)


def findTenure(folder):
    cDir = "public/data/" + folder + "/commits/"
    tenures = {}

    file =  "allUsers.json"
    with open(cDir + file, 'r') as f:
        data = json.loads(f.read())

    for user in data:
        commitInfo = data[user]
        tenures[user] = {}

        start = time.strptime("2099-01-01","%Y-%m-%d")
        end = time.strptime("2000-01-01","%Y-%m-%d")

        for item in commitInfo:
            date = item["date"][0:10]
            ts = time.strptime(date,"%Y-%m-%d")
            if(ts < start):
                start = ts

            if (ts > end):
                end = ts

        tenures[user]["start"] = str(start.tm_year)+"-"+"%02d" % start.tm_mon+"-"+"%02d"%start.tm_mday
        tenures[user]["end"] =  str(end.tm_year)+"-"+"%02d" %end.tm_mon+"-"+ "%02d" % end.tm_mday

        start = datetime.datetime(start.tm_year,start.tm_mon,start.tm_mday)
        end = datetime.datetime(end.tm_year,end.tm_mon,end.tm_mday)
        tenure = (end - start).days

        tenures[user]["tenure"] = tenure

    with open(cDir + "tenures.json", 'w') as f:
        json.dump(tenures,f)
