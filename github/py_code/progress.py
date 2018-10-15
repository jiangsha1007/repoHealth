import os

def writeTo(state,flag,f):
    if(flag == 'start'):
        f.writelines("Downloading the "+state + "......")
    elif(flag == "end"):
        f.writelines("Complete.")

def progress(repo,state,flag):
    file = "public/data/" + repo + "/progress"

    if(state == 'analyze'):
        with open(file,'a') as f:
            if(flag == 'start'):
                f.writelines("\nAnalyzing the details......")
            elif(flag == "end"):
                f.writelines("Complete.")
    if(state == 'commits'):
        with open(file,'a') as f:
            writeTo(state, flag, f)
    if(state == 'issues'):
        with open(file,'a') as f:
            if(flag == "start"):
                f.writelines("\n")
            writeTo(state, flag, f)
    if(state == 'comments'):
        with open(file,'a') as f:
            if(flag == "start"):
                f.writelines("\n")
            writeTo(state, flag, f)
'''
items=["commits","issues","comments","analyze"]
repo = "nlohmann/json"
for item in items:
    progress(repo,item,"start")
    progress(repo,item,"end")
'''
