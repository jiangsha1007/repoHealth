# 统计所有开发者的Id
import json
import re
import os
import time
import datetime
import calendar

def findAllUsersId(repo):
    repos = repo.split(sep="/")
    organ = repos[0]
    folder = repos[1]

    cDir = "public/" + folder + "/"

    allUsersId = []
    allUsers = {}

    for year in range(2008,2019):
        for month in range(1,13):
            prefix = cDir + str(year) + "-" + "%02d" % month
            with open(prefix + "-originalCommits.json",'r') as f:
                data = json.loads(f.read())

                for item in data:
                    if (item["author"]):
                        id = item["author"]["id"]
                        if (id not in allUsers):
                            allUsers[id] = 0
                            allUsersId.append(id)

    with open(cDir  + "allUsersId.json",'w') as f:
        json.dump(allUsersId,f)
repos = ["d3/d3","airbnb/javascript","nlohmann/json"]
for item in repos:
    findAllUsersId(item)
