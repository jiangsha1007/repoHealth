import json
import attraction
import findTenure
import contribution
import ownership
import analyzeComments
import analyzeIssues

def analyzeCommits(repo,startYear,startMonth,endYear,endMonth):
    print("I am analyzeCommits.")
    cDir = "public/data/" + repo + "/commits/"


    attraction.merge(repo,endYear)

    findTenure.findTenure(repo)

    contribution.findCon(repo,startYear,startMonth,endYear,endMonth)

    contribution.getData(cDir,endYear)
    ownership.getOwnership(repo,endYear)
def analyze(repo,start,end):
    startYear = int(start[0:4])
    startMonth = int(start[5:7])
    endYear = int(end[0:4])
    endMonth = int(end[5:7])

    analyzeCommits(repo,startYear,startMonth,endYear,endMonth)
    analyzeIssues.analyzeIssues(repo,endYear)
    analyzeComments.analyzeComments(repo,endYear)

'''
paras = ["nlohmann/json","2008-01-01","2018-08-08"]
analyze(paras[0],paras[1],paras[2])
'''
