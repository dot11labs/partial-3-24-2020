from __future__ import print_function
import winpexpect
import requests
from time import sleep

#config for ASUS AX88U
deviceIP='192.168.1.105'
deviceUsername="admin"
devicePassword="password"
deviceRadio=[]
#deviceRadio='eth7'
#Please write in lowercase, e.g.: ssh, telnet, pal
deviceAccess='telnet'
	
#Custom Report label/value name
CRValueName=[]
originalLabelLength=0
deviceMode='Station'

def findStationMAC(child):
	global deviceRadio, CRValueName, originalLabelLength
	CRValueName=['STA CH', 'STA BSSID','STA RSSI0','STA RSSI1','STA RSSI2','STA RSSI3','STA RSSI AVG', 'STA PHY Rate', 'STA MCS', 'STA Device Radio', 'STA NSS', 'STA BW', 'STA Nrate']
	originalLabelLength=len(CRValueName)
	child.sendline('wl -i eth7 assoclist')
	try:
		child.expect('[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]', timeout=3)
		deviceRadio.append('eth7')		
	except:
		pass
	child.sendline('wl -i eth6 assoclist')
	try:
		child.expect('[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]', timeout=3)
		deviceRadio.append('eth6')
	except:
		pass
	
	CRValueName=CRValueName*len(deviceRadio)

def initAccess():
	global deviceRadio
	deviceRadio=[]
	print('{}-ing to {}'.format(deviceAccess, deviceIP))
	if deviceAccess=='ssh':
		child = winpexpect.winspawn('plink -{} {}@{} -pw {}'.format(deviceAccess, deviceUsername, deviceIP, devicePassword))
		try:
			child.expect('$')
		except:
			print("Timeout reached: First time ssh-ing into the device/device is offline")
			#child.expect('(y/n)', timeout=3)
			child.sendline('y')
			child.expect('#|$', timeout=10)            
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
	try:
		if deviceAccess!='pal' or deviceAccess!='ssh' : 
			if i==0:
				child.sendline('wl -i {} channel'.format(devRadio))
				child.expect('current mac channel')
				child.expect('\d+')
				data = int(child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==1:
				child.sendline('wl -i {} bssid'.format(devRadio))
				child.expect('bssid')
				child.expect('[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]')
				data = (child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==2:
				child.sendline('wl -i {} phy_rssi_ant'.format(devRadio))
				child.expect('rssi\[0\]')
				child.expect('-\d+')
				data = int(child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==3:
				child.expect('rssi\[1\]')
				child.expect(' -\d+')
				data = int(child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==4:
				child.expect('rssi\[2\]')
				child.expect(' -\d+')
				data = int(child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==5:
				child.expect('rssi\[3\]')
				child.expect(' -\d+')
				data = int(child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==6:
				child.sendline('wl -i {} phy_rssi_ant'.format(devRadio))
				child.expect('rssi\[0\]')
				child.expect('-\d+')
				data1 = int(child.after)
				child.expect('rssi\[1\]')
				child.expect('-\d+')
				data2 = int(child.after)
				child.expect('rssi\[2\]')
				child.expect('-\d+')
				data3 = int(child.after)
				child.expect('rssi\[3\]')
				child.expect('-\d+')
				data4 = int(child.after)
				data=float(data1+data2+data3+data4)/4
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==7:
				child.sendline('wl -i {} rate'.format(devRadio)) 
				child.expect('wl -i {} rate'.format(devRadio))
				child.expect('\d+.\d|\d+')
				data = (child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==8:
				child.sendline('wl -i {} nrate'.format(devRadio)) 
				child.expect('wl -i {} nrate'.format(devRadio))
				child.expect('mcs|legacy rate')
				child.expect('\d+|\d.\d')
				data = (child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==9:
				print ('{}: '.format(CRValueName[i]),devRadio)
				return devRadio
			elif i==10:
				child.sendline('wl -i {} nrate'.format(devRadio))
				child.expect('wl -i {} nrate'.format(devRadio))
				temp=child.before
				if 'Nss' in temp:
					child.expect('Nss')
					child.expect('\d')
					data = (child.after)
					print ('{}: '.format(CRValueName[i]),data)
					return data
				else:
					data = '#N/A'
					print ('{}: '.format(CRValueName[i]),data)
					return data
			elif i==11:
				child.sendline('wl -i {} nrate'.format(devRadio))
				child.expect('wl -i {} nrate'.format(devRadio))
				temp=child.before
				if 'bw' in temp:
					child.expect('bw')
					child.expect('\d\d|\d\d\d')
					data = (child.after)
					print ('{}: '.format(CRValueName[i]),data)
					return data
				else:
					data = '#N/A'
					print ('{}: '.format(CRValueName[i]),data)
					return data
			elif i==12:
				child.sendline('wl -i {} nrate'.format(devRadio))
				child.expect('wl -i {} nrate\r\n'.format(devRadio))
				child.expect('\nadmin')
				data = (child.before)
				print ('{}: '.format(CRValueName[i]),data)
				return data

		return "#N/A"
	except:
		print("ERROR - Timeout reached")
		print("Error on child.before:", child.before,"& child.after:",child.after)
		data = "#ERROR"
		print ('{}: '.format(CRValueName[i]),data)
		return data


