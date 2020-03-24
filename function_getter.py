from __future__ import print_function
import requests, pexpect
import json
import csv
from api.octoBox_devices import *

#-----Specifically for Linux------
def setAllAtten(mode):# Works for Windows too
	#atten here refers to dB
	if mode=='max':
		atten="90.0"
	elif mode=='min' or mode=='zero' or mode==0:
		atten="0"
	else:
		print("Invalid mode for setAllAtten: Please pick between max and min/zero")
		return 0
	js={"atten1":atten, "atten2":atten, "atten3":atten,"atten4":atten} 
	headers={
		'Content-Type': 'application/json'
	}
	#url=['169.254.20.11', '169.254.20.16', '169.254.20.18', '169.254.22.22', '169.254.20.26']
	url=['169.254.20.11', '169.254.20.18', '169.254.22.22']
	try:
		for i in range(len(url)):
			requests.post('http://'+url[i]+'/api/quadAtten', json=js, headers=headers)
	except:
		print("Setting quadAtten "+url[i]+" to "+atten+"dB failed!")
	
	mpe='169.254.23.2'
	if mode=='max':
		atten="63.0" #For MPE
	js={"atten1":atten, "atten2":atten, "atten3":atten,"atten4":atten} 
	try:
		requests.post('http://'+mpe+'/api/MPE', json=js, headers=headers)
	except:
		print("Setting MPE "+mpe+" to "+atten+"dB failed!")

def setAtten(ip, atten, mode): #works for Windows too
	#atten here refers to dB
	js={"atten1":atten, "atten2":atten, "atten3":atten,"atten4":atten} 
	headers={
		'Content-Type': 'application/json'
	}
	mode='MPE' if mode=='mpe' else mode
	try:
		requests.post('http://'+ip+'/api/'+mode, json=js, headers=headers)
	except:
		print("Setting {} {} to {} dB failed!".format(mode, ip, atten))

def parseCSVtoList(path):
	with open(path, 'r') as f:
		reader=csv.reader(f)
		return list(reader)

def obtainRealDataAndLabels(json):
	index=-1
	for i in range(len(json)):
		if len(json[i])>0:
			if json[i][0]=='Step Index':
				index=i
				break
	if index==-1:
		print("Error: Throughput doesn't exist in CSV file!")
		return index
	return json[index:]

def obtainRealData(json):
	index=-1
	for i in range(len(json)):
		if len(json[i])>0:
			if json[i][0]=='Step Index':
				index=i
				break
	if index==-1:
		print("Error: Throughput doesn't exist in CSV file!")
		return index
	return json[index+1:]

def createTraffic(config, testId, octobox, station, traffic_config):

	fromObj = config['address']
	toObj = config['address2']
	tp = config['name']
	from_, errors = octobox.endpoint.readByAddress(fromObj)
	to_, errors = octobox.endpoint.readByAddress(toObj)
	print ('From '+config["address"]+', to '+config["address2"])

	#Only works for creating stations, not for server
	if from_==None:
		print('From: Creating endpoint '+fromObj)
		epFrom={'address':fromObj, 'managementAddr':station['stamgmt_ip'], 'name':fromObj+'@Pal'} #for iperf3, delete managementAddr
		from_, errors =octobox.endpoint.create(epFrom)
	if to_==None:
		print('To: Creating endpoint '+toObj)
		epTo={'address':toObj, 'managementAddr':station['stamgmt_ip'], 'name':toObj+'@Pal'} #for iperf3, delete managementAddr
		to_, errors =octobox.endpoint.create(epTo)
	# Setup for the trafficPair
	trafficPairInput = {
		'testId': testId,
		'name': tp,
		'from': from_['id'],
		'to': to_['id'],
		'active': True,
		'length':traffic_config['length'],
		'window':traffic_config['window'],
		'udp':traffic_config['udp'],
		'bitrate':traffic_config['bitrate']
	}
	# If this is TCP, then add parallel
	if not traffic_config['udp']:
		trafficPairInput['parallel']=traffic_config['parallel']
	# Create trafficPair
	return octobox.trafficPair.create(trafficPairInput)

#---------------------------------
def iperf3JSON(path):
	try:
		return json.loads(open(path).read())
	except:
		print ('Error: json file not found')
		return 'Error: json file not found'

def logIn(child, customReport, cust):
	for i in range(len(customReport)):
		if customReport[i]==True:
			child.append(cust[i].initAccess())
		else:
			child.append('')

def logOut(customReport, child, cust):
	for i in range(len(customReport)):
		if customReport[i]==True:
			print("Killing customReport{}".format(i+1))
			#Specifically for BGW210 or other device that has multi-level exits
			cust[i].exit(child[i])
			###############################
			killpexpect(child[i])
	for i in range(len(customReport)):
		child.pop()

def checkAtten(address, attenMode):
	try:
		if attenMode=='quadAtten':
			data=requests.get("http://{}/api/quadAtten".format(address)).json()['atten1']
		elif attenMode=='mpe':
			data=requests.get("http://{}/api/MPE".format(address)).json()['atten1']
		return float(data)
	except:
		print("checkAtten error")
		return "#CheckAtten Error"

def createAtten(start,stop,step,data):
	while start<=stop:
		data.append(start)
		start+=step

def runTest(id):
	requests.post("http://{}/api/1/public/test/run/{}".format('localhost:5000', id))
def stopTest(id):
	requests.put("http://{}/api/1/public/test/stop/{}".format('localhost:5000', id))
def emptyArray(arr):
	for i in arr:
		if type(arr[i]) is list:
			del arr[i][:]

def emptyArraySingle(*arr):
	for x in arr:
		del x[:]

def updateTraffic(host,configID,configJSON,clientID,serverID,trafficPair,trafficCounter, testNumber,trafficPairsUnderTest, iperfActive, iperfProtocol, iperfOfferedLoad, iperfStreams, iperfDatagramSize, iperfTCPWindowSize):
		# Delete all existing traffic pair and add new one
		deleteAllTraffic(host, configID, configJSON)
		length=len(trafficPairsUnderTest[testNumber])
		for i in range(length):
			temp=99
			for x in range(len(trafficPair)):
				if trafficPair[x][0]==trafficPairsUnderTest[testNumber][i]:
					temp=x
					break
			try:
				config_addTrafficPair(host,	configID, serverID[temp],clientID[temp],trafficPair[temp][0], iperfActive, iperfProtocol, iperfOfferedLoad, iperfStreams, iperfDatagramSize, iperfTCPWindowSize)
			except:
				print("Error occurred/Incorrect name value is inputted: ", sys.exc_info()[0])

def initializeTrafficID(host, trafficPair, trafficCounter, serverID, clientID):
	for i in range(len(trafficPair)):
		serverID.append(device_getDeviceByIPAddress(host,trafficPair[i][1]))
		clientID.append(device_getDeviceByIPAddress(host,trafficPair[i][2]))

def getConfigJSON(host, configID):
	return requests.get('http://{}/api/1/public/config/get/{}'.format(host, configID), timeout=10).json()['apiPayload']

def deleteAllTraffic(host, configID, config):
	#e.g. to remove all pairs:
	config['traffic']['items'] = []
	#3. put modified config back onto the server
	config_update_status = requests.put('http://{}/api/1/public/config/update/{}'.format(host, configID),json=config,timeout=10)

def getTestJSON(name):
	json = requests.get("http://localhost:5000/api/1/public/test/search?name={}".format(name))
	json=json.json()['apiPayload']
	for x in range(len(json)):
		if json[x]['name']==name:
			return json[x]

def getConfigID(json):
	return json['config_id']

def getTestID(json):
	return json['_id']

def getListJSON(id):
	json = requests.get("http://{}/api/1/public/test/list".format('localhost:5000'))
	json=json.json()['apiPayload']
	for x in range(len(json)):
		if json[x]['_id']==id:
			return json[x]
	return '' #Shouldn't ever get here; if it does, test ID doesn't exist

#The value of how many degree per step
def getStep(json):
	#status = requests.get("http://{}/api/1/public/test/list".format('localhost:5000'))
	#x=status.json()['apiPayload'][0]['config_id']['rotation']['step']
	return json['config_id']['rotation']['step']

def getStart(json):
	return json['config_id']['rotation']['start']

def getIteration(json):
	#status = requests.get("http://{}/api/1/public/test/list".format('localhost:5000'))
	#x=status.json()['apiPayload'][0]['config_id']['iterationDuration']
	return json['config_id']['iterationDuration']

def getThroughput(json):
	return json['result']['testRuns'][-1]['measurements'][-1]['average']

def getTrafficName(json):
	x=json['config_id']['traffic']['items']
	#Search for the currently selected traffic. Only work for 1 traffic for now
	for i in range(len(x)):
		if x[i]['active']==True:
			return x[i]['name']
	return "#NoTrafficIsSelected?#"

def getRunningStatus():
	x = requests.get("http://{}/api/1/public/test/status".format('localhost:5000')).json()['apiPayload']['isRunning']
	return x

# For octoscope turntable only
def getTurntableStatus(turntable):
	status = turntable.get_info()
	x = status.json()['status']
	return x
# For octoscope turntable only
def getPosition(turntable):
	info = turntable.get_info()
	x = int(info.json()['pos'])
	return x

def getJSON(id):
	x=requests.get("http://{}/api/1/public/test/export/json/{}".format('localhost:5000',id))
	return x.json()

def parseJSON(dataList):#pos, throughput, json):
	try:
		x=dataList["json"]["apiPayload"]["result"]["testRuns"][-1]["measurements"]
		for i in range(len(x)):
			dataList["position"].append(x[i]["position"])
			dataList["throughput"].append(x[i]["average"])
	except:
		print("parseJSON error")


def getTestName(json):
	return json["apiPayload"]["name"]

def killpexpect(child):
	try:
		if not isinstance(child,str):
			child.sendline('exit')
			child.terminate()
	except:
		print ("Error occurred when attempting to exit customReport. Presumably disconnected.")


def printLog(newPosition, numberOfTest, child, throughputData, trafficScript, step, testDuration, delay, throughputProtocol, testWithRvr, totalRvrSteps):
	print(trafficScript[numberOfTest])
	print ('Position: ',newPosition)
	print ('Protocol: ',throughputProtocol)
	#print("step: {}, newPosition: {}, len(trafficScript): {}, numberOfTest: {}, testDuration: {}, delay: {}".format(step, newPosition, len(trafficScript), numberOfTest, testDuration, delay))
	if testWithRvr:
		totalTest=totalRvrSteps*len(trafficScript)-numberOfTest
	else:
		totalTest=((360/step)-newPosition/step)*len(trafficScript)-numberOfTest
	time=(testDuration+delay)*totalTest
	print('Time remaining:', time/60,"mins",time%60,"sec")
	#print('')

def printLog2(throughputData, win_rssi, enableWindowsRSSI):
	totalTP=0
	for i in range(len(throughputData[-1])):
		totalTP+=float(throughputData[-1][i])
		print('Throughput pair {}:'.format(i+1),throughputData[-1][i],'Mbps')
	print('Total throughput:', totalTP, 'Mbps')
	if enableWindowsRSSI:
		print('Windows RSSI:', win_rssi)
	print('')

def rotateHome(turntable, turntableAP, turntableClient, pos, ttAP, ttClient, ttAPType, ttClientType):
	turntable.init()
	for i in range(len(ttAP)):
		turntableAP.append(Turntable(ttAP[i], ttAPType[i]))
		turntableAP[i].init() # Initialize FOLLOWER table to 0 and enable its status (if it's first time)
	for i in range(len(ttClient)):
		turntableClient.append(Turntable(ttClient[i], ttClientType[i]))
		turntableClient[i].init() # Initialize FOLLOWER table to 0 and enable its status (if it's first time)

def rotateAll(turntable, turntableAP, turntableClient, pos, ttAP, ttClient):
	turntable.set_position(pos)
	for i in range(len(ttAP)):
		turntableAP[i].set_position(-pos)
	# For Client, turn clockwise
	for i in range(len(ttClient)):
		turntableClient[i].set_position(pos)

def delayedRotation(turntable, turntableAP, turntableClient, pos, ttAP, ttClient, trainingTime):
	sleep(trainingTime)
	rotateAll(turntable, turntableAP, turntableClient, pos, ttAP, ttClient)
		
def setRotationSpeed(turntable, turntableAP, turntableClient, vel, ttAP, ttClient):
	turntable.set_velocity(vel)
	for i in range(len(ttAP)):
		turntableAP[i].set_velocity(vel)
	# For Client, turn clockwise
	for i in range(len(ttClient)):
		turntableClient[i].set_velocity(vel)

def exitTurntable(turntable, turntableAP, turntableClient, ttAP, ttClient):
	turntable.exit()
	for i in range(len(ttAP)):
		turntableAP[i].exit()
	# For Client, turn clockwise
	for i in range(len(ttClient)):
		turntableClient[i].exit()


class Turntable ():
	'''this class operates a turntable'''
	def __init__(self,address,ttType,action="pos",enable="1",pos_target="0",vel_target="5000"):
		if ttType=='octoscope':
			while True:
				try:
					self.address=address
					self.data=requests.get("http://{}/api/turntable".format(self.address))
					self.action=action
					self.enable=enable
					self.pos_target=pos_target
					self.vel_target=vel_target
					self.ttType=ttType
					break
				except:
					print('Octoscope: A problem with establishing connection to turntable {}. Retrying again in 1 second.'.format(self.address))
					sleep(1)
		elif ttType=='dot11':
			self.ttType=ttType
			self.address=address
			self.vel_target='medium2'
			self.fileName='turntableControl'
			self.position=0
			import platform
			if platform.system()=='Windows':
				import winpexpect
				self.child = winpexpect.winspawn('plink -{} {}@{} -pw {}'.format('ssh', 'pi', self.address, 'raspberry'))
			else:
				self.child = pexpect.spawn('{} {}@{} -pw {}'.format('ssh', 'pi', self.address, 'raspberry'))
			try:
				self.child.expect('$')
			except:
				print("Timeout reached: First time ssh-ing to raspberry/raspberry is offline")
				#child.pexpect('(y/n)', timeout=3)
				self.child.sendline('y')
				self.child.expect('#|$', timeout=10)
		else:
			print("Please enter the proper turntable type (ttType) to either dot11 or octoscope")

	def init(self):
		if self.ttType=='octoscope':
			pos=self.get_position()
			if pos>180 or pos<-180:
				self.set_position(0)
			else:
				post={
					"action":"home",
					"enable":"1"
				}
				requests.post("http://{}/api/turntable".format(self.address),json=post)
		elif self.ttType=='dot11':
			if self.position>0:
				self.child.sendline('python {}.py {} {} {} {}'.format(self.fileName, 360, 'fast', 'ccw', 'home')) #Was self.vel_target instead of 'fast'
			elif self.position<0:
				self.child.sendline('python {}.py {} {} {} {}'.format(self.fileName, 360, 'fast', 'cw', 'home')) #Was self.vel_target instead of 'fast'
			self.position=0
		else:
			print("Please enter the proper turntable type (ttType) to either dot11 or octoscope")
	
	def set_velocity(self, vel):
		self.vel_target=vel
	
	def set_position(self,pos_target):
		if self.ttType=='octoscope':
			'''this method will set the turntable to the given pos_target'''
			if pos_target > 720:
				raise NameError('Position may not exceed 720')
			set_position_submission={
				"action":"pos",
				"enable":"1",
				"pos_target":pos_target,
				"vel_target":self.vel_target
			}
			x = requests.post("http://{}/api/turntable".format(self.address),json=set_position_submission)
			return x
		elif self.ttType=='dot11':
			pos=int(pos_target)
			temp=''
			if pos>self.position: # Means go CW
				temp='cw'
				pos-=self.position
			elif pos<self.position:
				temp='ccw'
				pos-=self.position
				pos=abs(pos)
			else:
				#if current position is equals to target position, do nothing
				return ''
			self.position=int(pos_target)
			self.child.sendline('python {}.py {} {} {}'.format(self.fileName, pos, self.vel_target, temp))
		else:
			print("Please enter the proper turntable type (ttType) to either dot11 or octoscope")

	def get_position(self):
		if self.ttType=='octoscope':
			return int(self.get_info().json()['pos'])
		elif self.ttType=='dot11':
			return self.position
		else:
			print("Please enter the proper turntable type (ttType) to either dot11 or octoscope")
			return ''
	def get_info(self):
		if self.ttType=='octoscope':
			'''this method will get return the info on the turntable'''
			x=requests.get("http://{}/api/turntable".format(self.address))
			return x
		elif self.ttType=='dot11':
			return 'no info yet..?'
		else:
			print("Please enter the proper turntable type (ttType) to either dot11 or octoscope")
			return ''
	def get_status(self):
		if self.ttType=='octoscope':
			x=requests.get("http://{}/api/1/public/test/status".format('localhost:5000'))
			return x
		elif self.ttType=='dot11':
			self.child.sendline('gpio read 7')
			self.child.expect('gpio read 7')
			self.child.expect('\d')
			return int(self.child.after)
		else:
			print("Please enter the proper turntable type (ttType) to either dot11 or octoscope")
			return ''

	def exit(self):
		if self.ttType=='dot11':
			self.child.sendline('exit')
			self.child.terminate()
			self.child.close()
