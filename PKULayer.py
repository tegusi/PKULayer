import requests,datetime,dateutil.tz
import gpxpy.gpx,gpxpy
import json, os.path, getpass

def second_to_time(second):
    return datetime.time(hour=int(second/3600),minute=int((second%3600)/60),second=(second%60))

class Record:
    def __init__(self):
        self.points = []
        self.date = datetime.datetime.now(tz=dateutil.tz.tzoffset(None,0))
        self.duration = ''

    def load(self,path):
        if os.path.splitext(path)[1] != '.gpx':
            print('Only GPX file is supported.')
            return False
        with open(path,'r') as f:
            try:
                gpx = gpxpy.parse(f)
                for track in gpx.tracks:
                    for segment in track.segments:
                        start_time = segment.points[0].time
                        for point in segment.points:
                            self.points.append((point.longitude,point.latitude))
                            end = point.time
                self.duration = end.timestamp()-start_time.timestamp()
            except gpxpy.gpx.GPXXMLSyntaxException:
                print("GPX file is not valid")
                return False
        return True
class Track:
    def __init__(self,duration,distance,valid):
        self.duration = duration
        self.distance = distance
        self.valid = valid

class TrackInfo:
    success = ""
    data = []

class User:

    def __init__(self,id,password):
        self.id = id
        self.password = password
        self.authentication_code = ''
        self.history = TrackInfo()

    def __str__(self):
        return self.id

    def login(self):
        headers = {"User-Agent": "PKURunner/1.0 (iPhone; iOS 10.2.1; Scale/2.00)"}
        payload = {'appid':'portal','password':self.password,'userName':self.id,'redirUrl':'portal.pku.edu.cn/portal2013/login.jsp/../ssoLogin.do'}
        s = requests.post("https://iaaa.pku.edu.cn/iaaa/oauthlogin.do",headers=headers,data=payload)
        raw_data = json.loads(s.text)
        self.authentication_code = raw_data['token']
        payload = {'access_token':self.authentication_code,'id':self.id}
        s = requests.post("http://162.105.205.61:10201/user".format(str(self.id)), headers=headers, data=payload)
        response  = json.loads(s.text)
        print("Welcome, {} logined succesfully".format(response['data']['name']))

    def get_record_info(self):
        headers = {'Authorization': self.authentication_code,
                   "User-Agent": "PKURunner/1.0 (iPhone; iOS 10.2.1; Scale/2.00)"}
        s = requests.get("http://162.105.205.61:10201/record/{}".format(str(self.id)),headers=headers)
        response = json.loads(s.text)
        for record in response['data']:
            self.history.data.append(Track(second_to_time(record['duration']),record['distance'],record['verified'] == True))
        total_dis = 0
        for record in self.history.data:
            if record.valid:
                total_dis += record.distance
        print("You have accomplished {}km".format(total_dis/1000))

    def upload(self,record):
        if not isinstance(record,Record):
            print("Format of track is not correct.")
        route = "["
        for point in record.points:
            route += "[{},{}],".format(point[0],point[1])
        route = route[:-1] + "]"
        payload = {
            'date': record.date.isoformat(timespec='seconds',sep=' '),
            'detail': route,
            'distance': 2333,
            'duration': int(record.duration),
            'userId': self.id
        }
        headers = {'Authorization':self.authentication_code,"User-Agent": "PKURunner/1.0 (iPhone; iOS 10.2.1; Scale/2.00)"}
        s = requests.post("http://162.105.205.61:10201/record/{}".format(str(self.id)),headers=headers,data=payload)
        response = json.loads(s.text)
        if response["success"] == True:
            print("Success!")
        else:
            print("Failed when uploading...")

print("Please input your id and password")
id = input("Student ID: ")
password = getpass.getpass("Pasword: ")
u = User(1500012739,'xTcwSqn4eGDt')
u.login()
u.get_record_info()
rec = Record()
path = input("Please input file: ")
while not rec.load(path):
    path = input("Please input file: ")
u.upload(rec)