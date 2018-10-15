import json
import getURL
import shutil
import os
import divideCommentsMonth
import requests
from urllib2 import urlopen
import urllib2
import re
import time

def getAllComments(repo):
    cDir = "public/data/" + repo+ "/" + "comments/"
    if(os.path.exists(cDir)):
        shutil.rmtree(cDir)
    os.makedirs(cDir)
    url = 'https://api.github.com/repos/'+repo+ \
            "/comments?access_token=8f6085fc4cf4b501a7ccad1a3aadc3f98f51384a"
    commentResponse = getURL.getURL(url)
    commentsData = json.loads(commentResponse.data)

    '''
    urlRequest = request.Request(url)
    urlResponse = request.urlopen(urlRequest)
    commentsData = json.loads(urlResponse.read().decode("utf-8"))
    '''
    page = 1

    with open(cDir + "allComments-" + str(page) + ".json","w") as f:
        json.dump(commentsData,f)

    headData = str(commentResponse.headers)
    while True:
        listLink = re.findall(r'(?<=<).[^<]*(?=>; rel=\"next)',headData)
        print("listLink: " , listLink)
        if(listLink):
            nextLink = listLink[0]
            print("nextLink: " , nextLink)
            time.sleep(1)
            page += 1
            commentResponse = getURL.getURL(nextLink)
            commentsData = json.loads(commentResponse.data)
            '''
            commentsResponse = request.urlopen(nextLink)
            commentsData = commentsResponse.read().decode('utf-8')
            commentsData = json.loads(commentsData)
            '''
            with open(cDir + "allComments-" + str(page) + ".json","w") as f:
                json.dump(commentsData,f)

            headData = str(commentResponse.headers)

        else:
            break


def downloadComments(repo,startDate,endDate):

    getAllComments(repo)

    endDate = time.strptime(endDate[0:10],"%Y-%m-%d")
    endYear = endDate.tm_year
    divideCommentsMonth.divideCommentsMonth(repo,endYear)
