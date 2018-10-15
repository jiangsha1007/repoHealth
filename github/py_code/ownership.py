# -*- coding: utf-8 -*
# 寻找每个文件被几位开发者修改过 获得 AF 值
import json

# 文件数*修改该文件的人数 / 文件数
def getOwnership(folder,endYear):
    cDir = "public/data/" + folder + "/commits/"
    result = {}
    currentOwns = -1
    A = 0
    B = 0
    for year in range(2008,endYear+1):
        ownerships = {}
        counts = {}
        thisYearOwns = []

        for month in range(1,13):
            prefix = cDir + str(year) + "-" + "%02d" % month
            file = prefix +  "-modifiedFiles.json"

            with open(file,'r') as f:
                data = json.loads(f.read())
                for item in data:
                    filename = item["filename"]
                    user = item["user"]
                    if (filename not in counts):
                        counts[filename] = 0
                        B += 1
                    if ( filename not in ownerships):
                        ownerships[filename] = {}
                    if ( user not in ownerships[filename]):
                        ownerships[filename][user] = 1
                        counts[filename] += 1
                        A +=1

            if( B != 0):
                currentOwns = round(A/B,2)
                 # %s-%d" % (folder,year)
            thisYearOwns.append(currentOwns)
        if(B!=0):
            result[str(year)] = thisYearOwns

    with open(cDir + "ownership.json",'w') as f:
        json.dump(result,f)
