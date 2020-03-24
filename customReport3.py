from __future__ import print_function
import winpexpect
import requests
from time import sleep

#config for 11ax laptop
deviceIP='192.168.1.202'
deviceUsername="dot11"
devicePassword="d0t11l@bs"
deviceRadio=[]
#deviceRadio='eth7'
#Please write in lowercase, e.g.: ssh, telnet, pal
deviceAccess='ssh'
	
#Custom Report label/value name
CRValueName=[]
originalLabelLength=0
deviceMode='Station'
dataP = []

def findStationMAC(child):
	global deviceRadio, CRValueName, originalLabelLength
	CRValueName=[ 'STA CH','STA Signal', 'STA Rx','STA Tx','STA BSSID']
	originalLabelLength=len(CRValueName)
	deviceRadio.append('1')		
	CRValueName=CRValueName*len(deviceRadio)

def initAccess():
	global deviceRadio
	deviceRadio=[]
	CRValueName=['STA CH','STA Signal', 'STA Rx','STA Tx','STA BSSID',]
	print('{}-ing to {}'.format(deviceAccess, deviceIP))
	if deviceAccess=='ssh':
		child = winpexpect.winspawn('plink -{} {}@{} -pw {}'.format(deviceAccess, deviceUsername, deviceIP, devicePassword))
		try:
			child.expect('>')
		#	sleep(1)
		except:
			print("Timeout reached: First time ssh-ing into the device/device is offline")
			#child.expect('(y/n)', timeout=3)
			child.sendline('y')
			child.expect('#|$|>', timeout=10)            
	elif deviceAccess=='telnet':
		child = winpexpect.winspawn('plink -{} {}'.format(deviceAccess, deviceIP))
		sleep(1)
		child.expect('ogin:', timeout=10)
		child.send('{}\r'.format(deviceUsername))
		#Need to add another line for case of password
		child.expect('Password:', timeout=10)
		child.send('{}\r'.format(devicePassword))
		#child.expect('>')
		#child.sendline('magic')
		#child.expect('MAGIC>')
		#child.sendline('!')
		#child.sendline('sh')
		child.expect('#')
	else:
		child=''
		print('ERROR: Please write deviceAccess label in lower case or appropriately')
	findStationMAC(child)
	return child

# Only for customReport that requires extra exit. If it should have nothing, delete everything and write: pass
def exit(child):
	pass
	
def getCustomReport(child,i): 
	iteration=int(i/originalLabelLength)
	i=i%originalLabelLength
	#print(iteration, i, originalLabelLength, len(CRValueName))
	devRadio=deviceRadio[iteration]
	if (len(dataP) >= 5 and i == 0):
		del dataP[:]
	try:
		if deviceAccess=='ssh':
			if i==0:
				child.sendline('netsh.exe wlan show interfaces')
				child.expect('BSSID')
			 	child.expect('[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]')
			 	data1 = (child.after)
				dataP.append(data1)
				
				child.expect('Channel')
				child.expect('\d+')
				data2 = int(child.after)
				dataP.append(data2)
				
				child.expect('Receive rate')
				child.expect('\d+')
				data3 = int(child.after)
				dataP.append(data3)
				
				child.expect('Transmit rate')
				child.expect('\d+')
				data4 = int(child.after)
				dataP.append(data4)
				
				child.expect('Signal')
				child.expect('\d+')
				data5 = (int(child.after)/2 - 100)
				dataP.append(data5)
				
				print ('{}: '.format(CRValueName[i]),data2)
				return data2
			elif i==1:
				#child.expect('Signal')
				#child.expect('\d+')
				#data = int(child.after)
				print ('{}: '.format(CRValueName[i]),dataP[4])
				return dataP[4]
			elif i==2:
				#child.expect('Receive rate')
				#child.expect('\d+')
				#data = int(child.after)
				#data='NA'
				print ('{}: '.format(CRValueName[i]),dataP[2])
				return dataP[2]
			elif i==3:
				#child.expect('Transmit rate')
				#child.expect('\d+')
				#data = int(child.after)
				#data='NA'
				print ('{}: '.format(CRValueName[i]),dataP[3])
				return dataP[3]
			elif i==4:
			 	#child.expect('BSSID')
			 	#child.expect('[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]')
			 	#data = (child.after)
				print ('{}: '.format(CRValueName[i]),dataP[0])
				return dataP[0]
		return "#N/A"
	except:
		print("ERROR - Timeout reached")
		print("Error on child.before:", child.before,"& child.after:",child.after)
		data = "#ERROR"
		print ('{}: '.format(CRValueName[i]),data)
		return data



