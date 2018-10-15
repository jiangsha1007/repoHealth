import time
import pandas as pd 
import certifi
import urllib3
from urllib3.exceptions import ReadTimeoutError, ConnectTimeoutError
import csv

def output_df(df, owner_name, repo_name):
    # print(df)
    for indexs in df.index:
        topic = df.loc[indexs].values[-1]
        json_file = open('result/{}.json'.format(topic), 'a')
        json_file.write('{}/{}\n'.format(owner_name, repo_name))
        json_file.close()

def try_read_data(data):
    try:
        return pd.read_json(data)
    except:
        return None

def read_data(data, owner_name, repo_name):
	# print(data)
	df = try_read_data(data)
	if df.empty:
		print("\tNot Reading")
		return False
	print("\tReading")
	output_df(df, owner_name, repo_name)
	return True

def try_wait(remain, st):
	print(remain)
	if 10 > int(remain):
		print('###### WAITING FOR LIMITATION ######')
		time.sleep(st + 3600 - time.time())
		new_st = time.time()
		return new_st
	if 4990 < int(remain):
		print('############ NEW HOUR ##############')
		new_st = time.time()
		return new_st
	return st

def find_repo_topics(url, owner_name, repo_name, st, u_id):
    try:
        r = http.request('GET', url, timeout=urllib3.Timeout(connect=2.0, read=4.0), retries=False,
                         headers=headers[u_id])
    except ReadTimeoutError:
        print("ReadTimeoutError")
    except ConnectTimeoutError:
        print("ConnectTimeoutError")
    except e:
        print(e)
    else:
        print(r.status)
        print(u_id)
        u_id = u_id + 1
        u_id = u_id % 5
        if r.status == 301:
            url = r.data.decode().split("url\": \"")[1].split("\"")[0]
            # d = try_read_data(r.data.decode())
            # url = d.loc[0].values[-2]
            print("Redirecting to {}".format(url))
            find_repo_topics(url, owner_name, repo_name, st, u_id)
        elif r.status == 404:
            print("{}\{} not found".format(owner_name, repo_name))
        elif r.status != 200:
            print("{}\{} other reason failed".format(owner_name, repo_name))
        else:
            new_st = try_wait(r.headers['X-RateLimit-Remaining'], st)
            if new_st != st:
                st = new_st
            read_data(r.data.decode(), owner_name, repo_name)
    return st, u_id

# http = urllib3.PoolManager()
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
accept = 'application/vnd.github.mercy-preview'

headers = [
			urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot1:sjtucit1'), \
			urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot2:sjtucit2'), \
			urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot3:sjtucit3'), \
			urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot4:sjtucit4'), \
			urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot5:sjtucit5') ]
for header in headers:
	header['Accept'] = accept

st = time.time()
u_id = 0
print("############ STARTING ############")


repo_info = csv.reader(open('E:\\软件生态系统\\processed_data\\name_vertex.csv', encoding='utf-8'))
count = 0
for row in repo_info:
    if count == 1:
        full_name = row[3].split("/")
        owner = full_name[0]
        name = full_name[1]
        print(owner, name)
        url = 'https://api.github.com/repos/{}/{}/topics'.format(owner, name)
        st, u_id = find_repo_topics(url, owner, name, st, u_id)
    else:
        count = 1