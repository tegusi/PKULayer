import requests,datetime,dateutil.tz,json,gzip,copy,time

def duplicate(times,data):
    '''
    Duplicate the record by first arg
    The data is captured from PB app and contains the route of 1.1 km approxiamately
    Args:
        times: integer
        data: original data
    '''
    start_time = int(data['locusrlist'][0]['locuslist'][0][0]['traintime'])
    end_time = int(data['locusrlist'][0]['locuslist'][0][-1]['traintime'])
    end_cnt = int(data['locusrlist'][0]['locuslist'][0][-1]['stepcount'])
    end_dis = float(data['locusrlist'][0]['locuslist'][0][-1]['distance'])
    now_time = int(time.time()) * 1000 + 42
    tmp = []
    base_data = copy.deepcopy(data['locusrlist'][0]['locuslist'][0])
    for loc in base_data:
        for k in range(2,times+1):
            loc_ = copy.deepcopy(loc)
            loc_['traintime'] = int(loc['traintime']) - start_time + (k - 1) * (end_time - start_time) + k * 1000 + now_time
            loc_['stepcount'] = '{:.6f}'.format(int(loc['stepcount']) + (k-1) * end_cnt)
            loc_['distance'] = '{:.6f}'.format(float(loc['distance']) + (k-1) * end_dis)
            tmp.append(loc_)

    for loc in data['locusrlist'][0]['locuslist'][0]:
        loc['traintime'] = int(loc['traintime']) - start_time + now_time

    data['locusrlist'][0]['cal'] = int(data['locusrlist'][0]['cal']) * k
    data['locusrlist'][0]['locuslist'][0] += tmp
    data['locusrlist'][0]['locuslist'][0].sort(key=lambda x:x['traintime'])
    data['locusrlist'][0]['locuslist'][1][0] = tmp[-1]
    data['locusrlist'][0]['locuslist'][0].pop()
    data['locusrlist'][-1]['distance'] = '{:.2f}'.format(k * end_dis)
    data['locusrlist'][-1]['duration'] = '{:.2f}'.format(k * float(data['locusrlist'][-1]['duration']) )
    return data

id = input("Your student ID:")
pwd = input("Your password(default student ID):")
times = input("Distance you need(1.3*k), just input k:")
headers = {"User-Agent": "PB/1.8.5 (iPhone; iOS 11.1; Scale/2.00)",
           "Content-Type": "application/json",}
payload = {'pwd':pwd,'studentNo':id}
s = requests.post("http://www.biggerfitness.cn/biggerbuss/account/pkulogin.do",
                  headers=headers,
                  data=json.dumps(payload))
token = json.loads(s.content)['data']['token']
biggerId = json.loads(s.content)['data']['id']
headers = {"User-Agent": "PB/1.8.5 (iPhone; iOS 11.1; Scale/2.00)","Content-Encoding": "gzip"}
payloads = {'token':token, 'biggerId':biggerId}


# file_name = input("Please input filename:")
file_name = "54.json"
with open(file_name,'r') as f:
    data = json.load(f)

data = duplicate(int(times),data)
data['token'] = token
data['biggerId'] = biggerId
request_body = gzip.compress(json.dumps(data).encode('utf-8'))

s = requests.post("http://www.biggerfitness.cn/biggerbuss/newtrain/andfreetrainingzip.do",headers=headers,files={"file":request_body})

if json.loads(s.content)['state'] == 0:
    print("Upload successful.")
else:
    print("Upload failed.")
