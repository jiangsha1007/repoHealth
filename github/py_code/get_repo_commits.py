import time
import pandas as pd 
import certifi
import urllib3
from urllib3.exceptions import ReadTimeoutError, ConnectTimeoutError

def output_df(df, repo_name):

	# result_df = df[['login', 'id', 'node_id', 'url', 'type', 'site_admin']]
	# if 0 == count % 100:
		# print("----------------------------")
		# print("Open file {}:".format(count//100))
	# print("\t%10d"%count)
	json_file = open('{}.json'.format(repo_name), 'a')
	json_file.write(df.to_json(orient='records', lines=True))

	json_file.write('\n')
	json_file.close()

	# html_file = open('html2400/{}.html'.format(count//100), 'a')
	# html_file.write(result_df.to_html())
	# html_file.close()

def try_read_data(data):
    try:
        return pd.read_json(data, dtype={"login": str})
    except:
        return None

def read_data(data, repo_name):
	# print(data)
	df = try_read_data(data)
	if df is None:
		print("\tNot Reading")
		return False
	print("\tReading")
	output_df(df, repo_name)
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


# http = urllib3.PoolManager()
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'

headers = [	urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot1:sjtucit1'), \
			urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot2:sjtucit2'), \
			urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot3:sjtucit3'), \
			urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot4:sjtucit4'), \
			urllib3.util.make_headers(user_agent = user_agent, basic_auth = 'cit-bot5:sjtucit5') ]

url = 'https://api.github.com/repos/tensorflow/tensorflow/commits?per_page=100'
repo_name='tensorflow'
st = time.time()
# count = 280100

print("############ STARTING ############")

while 1:
	for header in headers:
		try:
			r = http.request('GET', url, timeout=urllib3.Timeout(connect=2.0, read=5.0), retries=False, headers=header)
		except ReadTimeoutError:
			print("ReadTimeoutError")
		except ConnectTimeoutError:
			print("ConnectTimeoutError")
		except e:
			print(e)
		else:
			print(r.status)
			new_st = try_wait(r.headers['X-RateLimit-Remaining'], st)
			if new_st != st:
				st = new_st
			if not read_data(r.data.decode(), repo_name):
				continue
			# count = count + 1
			url = r.headers['Link'].split('<')[1].split('>')[0]

