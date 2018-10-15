# -*- coding: utf-8 -*

import sys
import re
# from utils import Utilities
import re

import os
import pandas as pd
from pandas import *
import json
import getURL


def getRepoId(repo):
    url = 'https://api.github.com/repos/'+repo #"?access_token=8f6085fc4cf4b501a7ccad1a3aadc3f98f51384a"
    data = json.loads(getURL.getURL(url).data)
    print(data)
    return data["id"]
#getRepoId('d3/d3')
class Analyzer(object):
    def __init__(self):
        self.words = {}
        with open("public/words/positive.txt") as file:
            for line in file:
                self.words[line.rstrip()] = 1
        with open("public/words/negative.txt") as file:
            for line in file:
                self.words[line.rstrip()] = -1

    def analyze(self, message):
        score = 0
        found = 0

        i = 0
        WORD_SPLIT = r'"|(?:(?<=[a-z])[;\.])?\s+|(?:(?<=[a-z])[;\.])?$|(?!.[/(]\S)([^;\.\-\"\'+\w\s][^+\w\s]*(?:[-a-z]\b)?)|(?!.[/(]\S)((?:\b[a-z])?[^+\w\s]*[^;\.\-\"\'+\w\s])'
        parts = filter(lambda x: x != '' and x is not None, re.split(WORD_SPLIT, message.lower()))

        for w in parts:
            if w in self.words:
                score += self.words[w]
                found += 1

        label = score / float(found) if found != 0 else 0.0
        return (label, message)

def averagenum(num):
    nsum = 0.0
    for i in range(len(num)):
        nsum += num[i]
    return nsum / len(num)

def read_json(file):

    for jsonObject in file:
        try:
            # Allow control characters which are sometimes in the strings.
            data = json.loads(jsonObject, strict=False)
            print(data)
        except ValueError as e:
            raise(ValueError("Incorrect JSON string: '{}' with error '{}'".format(jsonObject, e)))
        for item in data:
            if "body" in item:
                if item['body'] != None:
                    item["body"] = item["body"].replace('\r\n', '\n')
                else: continue;
                fields = {}
                fields['body'] = item['body']
                yield fields

def main(repo,endYear):
    # repo_id = argv[0]
    repo_id = getRepoId(repo)
    cDir = "public/data/" + repo + "/comments/"
    # path = 'Data/' + str(repo_id)+'/'
    # repo_name = 'xx'

    outputname = cDir + 'res/' + 'data.csv'
    if not os.path.exists(cDir + 'res/'):
        os.makedirs(cDir + 'res/')

    analyzer = Analyzer()

    df = DataFrame(columns=('month', 'pos', 'mid', 'neg','average','num'))
    files = []
    flag = False
    for year in range(2008,endYear+1):
        for tmonth in range(1,13):
            file = "%d-%02d.json" % (year,tmonth)

            month = "%d-%02d" % (year,tmonth)

            scoreofmonth = []
            filename = cDir+file
            print("processing...", filename)

            with open(filename,'r') as f:
                tmpdata = json.loads(f.read())
                print(bool(tmpdata))

                if( (not flag) and (not tmpdata)):
                    print("no")
                    continue
                if(tmpdata):
                    flag = True
                print("yes")
            f = open(filename,'r')

            for data in read_json(f):
                print(data)
                if data['body'] == None: continue;
                (label, message) = analyzer.analyze(data["body"])
                scoreofmonth.append(label)

            sum = len(scoreofmonth)
            if sum == 0:
                tmp_df = DataFrame([[month, 0.0, 0.0, 0.0, 0.0, 0]], columns=('month', 'pos', 'mid', 'neg', 'average','num'))
            else:
                pos = len([item for item in scoreofmonth if item > 0.0])
                mid = len([item for item in scoreofmonth if item== 0.0])
                neg = len([item for item in scoreofmonth if item < 0.0])
                average = round(averagenum(scoreofmonth),4)
                tmp_df = DataFrame([[month, pos, mid, neg, average,int(sum)]], columns=('month', 'pos', 'mid', 'neg', 'average','num'))

            # print tmp_df
            df = df.append(tmp_df,ignore_index=True)

    # print df
    df.sort_values('month',inplace = True)
    df.to_csv(outputname,index=False,sep=',')

#repo = "nlohmann/json"

#endYear = 2018
def analyzeComments(repo,endYear):
    # 获取repoid
    id = getRepoId(repo)
    main(repo,endYear)
#analyComment(repo,endYear)
