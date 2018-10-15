# -*- coding: utf-8 -*-
#导入必要的模块
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
from scipy import interpolate
import matplotlib
from scipy.interpolate import spline
import pandas as pd
import csv
import matplotlib.gridspec as gridspec
import json
# plt.rcParams['font.sans-serif']=['SimHei']

repo_id = '4780086'
isExists=os.path.exists('repo_plot/')
if not isExists:
	os.makedirs('repo_plot/')
def get_name(repo_id):
	with open('repos_index2017.json','r') as load_f:
		data = json.load(load_f)
		for k,v in data.items():
			if v == int(repo_id):return k;
	return '#'


# f = open('repo_plot/repos.txt','r')
# lines = f.readlines()
# print (lines)

# f.close()
# if (repo_id+'\n') not in lines:
# 	f = open('repo_plot/repos.txt','a+')
# 	f.write(repo_id)
# 	f.write('\n')
# 	f.close()

global new_months
new_months = ['2017-01', '2017-02', '2017-03', '2017-04','2017-05','2017-06', '2017-07',
'2017-08', '2017-09', '2017-10', '2017-11', '2017-12', '2018-01', '2018-02', '2018-03', '2018-04',
'2018-05', '2018-06']
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2.-0.2, 1.03*height, '%d%%' % float(height*100))

def load_repo(repo_id):
	output_file = 'repo_info/'+repo_id+'.csv'
	isExists=os.path.exists('repo_info/')
	if not isExists:
		os.makedirs('repo_info/')

	with open(output_file,"w") as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(["month","pos","mid","neg"])

		for month in new_months:
			name = 'tmp/' + month + '.csv'
			df = pd.read_csv(name)

			score = df[df.repo.isin([repo_id])]
			sum = len(score.iloc[:,1])

			if sum == 0:
				writer.writerow([month, 0.0, 0.0, 0.0])
				continue

			pos = score[score['score'] > 0].score.count()
			mid = score[score['score']== 0].score.count()
			neg = score[score['score'] < 0].score.count()
			writer.writerow([month, pos/sum, mid/sum, neg/sum])

csvname = 'repo_info/' + repo_id + '.csv'
if os.path.exists(csvname) == False:
	load_repo(repo_id)

df = pd.read_csv(csvname)
pos = df.iloc[:,1].values
mid = df.iloc[:,2].values
neg = df.iloc[:,3].values

pos2017 = np.sum(pos[:12])
mid2017 = np.sum(mid[:12])
neg2017 = np.sum(neg[:12])

pos2018 = np.sum(pos[12:])
mid2018 = np.sum(mid[12:])
neg2018 = np.sum(neg[12:])

plt.figure(figsize=(8,8))

x =np.arange(0,len(new_months),1)
y =np.arange(0.0,1.0,0.1)
Y = [format(e,'.0%')  for e in y]

plt.subplot(311)
repo_name = get_name(repo_id)
if repo_name=='#':
	plt.title('Repo '+repo_id+' sentiment-analysis',fontweight = 'semibold')
else:
	plt.title(repo_name+' sentiment-analysis',fontweight = 'semibold')
plt.margins(0.08)

# plt.grid(linestyle = '--')

plt.xticks(x,new_months,rotation=25)
plt.yticks(y,Y,rotation=25)

plt.ylim(0.0,1.0)
plt.axhline(0, color='black')
a = plt.bar(x, pos+neg, width = 0.8, align = 'center',color = '#4CAF50', label = 'positive commits',edgecolor = 'white')
# plt.bar(x, mid, width = 0.8,align = 'center',facecolor = 'lightskyblue',  label = 'mid', edgecolor = 'black')
b = plt.bar(x, neg, width = 0.8, align = 'center',color = '#FF5252', label = 'negative commits', edgecolor = 'white')

i = 0
for j,k in zip(x,pos):
	if k==0.0:
		plt.text(j,k,'%d%%' % float(k*100),ha='center')
	else:
		plt.text(j,neg[i]+k*0.47,'%d%%' % float(k*100),ha='center')
	i += 1

for j,k in zip(x,neg):
	plt.text(j,k*0.45,'%d%%' % float(k*100),ha='center')

# plt.xlabel('Time')
# plt.ylabel('Ratio')
plt.legend(loc="upper right")


# def plot_line(repo_id):
Y = []
Y1 = []

empty_month = []
path = 'Result'

for file in os.listdir(path):
	if file == '.DS_Store': continue;
	if file[-4:]!='.csv': continue;

	name = path +'/'+file
	df = pd.read_csv(name)

	if len(df[df.repo.isin([repo_id])].average) == 0: #no commit history during this month
		empty_month.append(file)
		Y.append(0.0)
		continue

	score = df[df.repo.isin([repo_id])].average.item()
	Y.append(score)

X=range(len(new_months))
x =np.arange(0,len(new_months),1)
xnew = np.linspace(x.min(),x.max(),300) #300 represents number of points to make between T.min and T.max

Y_smooth = spline(X,Y,xnew)

plt.subplot(312)
plt.plot(xnew,Y_smooth,label='Average Rate')
plt.scatter(X,Y)
for a,b in zip(X,Y):
	plt.text(a,b,'%.2f'%b,fontsize=10)

plt.ylim(-1.0,1.0)

plt.axhline(0, color='black')
plt.xticks(X,new_months,rotation=25)
plt.grid()

# plt.xlabel('Time')
# plt.ylabel('Rate')
plt.legend(loc="upper right")

plt.subplot(325)
plt.title('2017',verticalalignment='bottom',fontsize=10)

labels = ['positive','neutral','negative'] #定义标签
sizes = [pos2017,mid2017,neg2017] #每块值
colors = ['#4CAF50','lightskyblue','#FF5252'] #每块颜色定义
explode = (0,0,0.03) #将某一块分割出来，值越大分割出的间隙越大
patches,text1,text2 = plt.pie(sizes,
                      explode=explode,
                      labels=labels,
                      colors=colors,
                      autopct = '%d%%', #数值保留固定小数位
                      shadow = True, #有阴影设置
                      startangle =90, #逆时针起始角度设置
                      pctdistance = 0.6) #数值距圆心半径倍数的距离
#patches饼图的返回值，texts1饼图外label的文本，texts2饼图内部的文本
# x，y轴刻度设置一致，保证饼图为圆形
plt.axis('equal')
plt.legend(loc="upper right",fontsize = 8)




if not (pos2018==mid2018==neg2018==0.0):
	plt.subplot(326)
	plt.title('2018',va='bottom',fontsize=10)
	labels = ['positive','neutral','negative'] #定义标签
	sizes = [pos2018,mid2018,neg2018] #每块值
	colors = ['#4CAF50','lightskyblue','#FF5252'] #每块颜色定义
	explode = (0,0,0.03) #将某一块分割出来，值越大分割出的间隙越大
	patches,text1,text2 = plt.pie(sizes,
	                      explode=explode,
	                      labels=labels,
	                      colors=colors,
	                      autopct = '%d%%', #数值保留固定小数位
	                      shadow = True, #有阴影设置
	                      startangle =90, #逆时针起始角度设置
	                      pctdistance = 0.6) #数值距圆心半径倍数的距离
	#patches饼图的返回值，texts1饼图外label的文本，texts2饼图内部的文本
	# x，y轴刻度设置一致，保证饼图为圆形
	plt.axis('equal')
	plt.subplots_adjust(hspace = 0.5)
	plt.legend(loc="upper right",fontsize = 8)
	plt.subplots_adjust(wspace = -0.1)
else:
	print ('No data in 2018.')


plt.savefig('repo_plot/'+repo_id+'.pdf')
plt.draw()
plt.pause(2)
plt.close()

def plotComments(repo):
	
