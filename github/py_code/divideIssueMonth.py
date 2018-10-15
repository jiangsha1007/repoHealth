import json
import re
import os
import time
import datetime
def divideIssueMonth(repo,endYear):
    repos = repo.split(sep="/")
    folder = repos[1]
    cDir = "public/data/" + repo+ "/" + "issues/"

    files = os.listdir(cDir)
    # print(files)
    pages=len(files)
    print(pages)
    pullRequests = []
    issues_created = {}

    for page in range(1,pages+1):
        print(page)
        with open(cDir + "allIssues-"+str(page)+".json",'r') as f:
            data = json.loads(f.read())

            for item in data:

                if ("pull_request" in item):
                    pullRequests.append(item)
                    continue
                date = item["created_at"];
                date=date[0:7]

                if (date not in issues_created):
                    issues_created[date] = []
                issues_created[date].append(item)


    with open(cDir + "pullRequests.json",'w') as f:
        json.dump(pullRequests,f)

    for year in range(2008,int(endYear) + 1):
        for month in range(1,13):
            date = "%d-%02d" %(year,month)
            if( date not in issues_created):
                with open(cDir + date + "-issues.json",'w') as f:
                    json.dump({},f)
            else :
                with open(cDir + date + "-issues.json",'w') as f:
                    json.dump(issues_created[date],f)
