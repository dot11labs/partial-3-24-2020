from __future__ import print_function
import winpexpect
import requests
from time import sleep

#config for Moto X
deviceIP='192.168.1.201'
deviceUsername='\"craig smith\"'
devicePassword='d0t11l@bs'
deviceRadio=[]
#deviceRadio='eth7'
#Please write in lowercase, e.g.: ssh, telnet, pal
deviceAccess='adb'
	
#Custom Report label/value name
CRValueName=[]
originalLabelLength=0
deviceMode='Station'

# def findStationMAC(child):
	# global deviceRadio, CRValueName, originalLabelLength
	# CRValueName=['STA CH',  'STA RSSI', 'STA PHY Rate']
	# originalLabelLength=len(CRValueName)
	# child.sendline('wl -i eth7 assoclist')
	# try:
		# child.expect('[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]', timeout=3)
		# deviceRadio.append('eth7')
	# except:
		# pass
	# child.sendline('wl -i eth6 assoclist')
	# try:
		# child.expect('[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]', timeout=3)
		# deviceRadio.append('eth6')
	# except:
		# pass
	
	# CRValueName=CRValueName*len(deviceRadio)
	
def setHeaders(child):
	global deviceRadio, CRValueName, originalLabelLength
	CRValueName=['STA CH', 'STA RSSI', 'STA Tx PHY Rate', 'STA BSSID']
	originalLabelLength=len(CRValueName)
	deviceRadio.append('wlan0')
	CRValueName=CRValueName*len(deviceRadio)

def initAccess():
	global deviceRadio
	deviceRadio=[]
	print('{}-ing to {}'.format(deviceAccess, deviceIP))
	if deviceAccess=='ssh':
		child = winpexpect.winspawn('plink -{} {}@{} -pw {}'.format(deviceAccess, deviceUsername, deviceIP, devicePassword))
		try:
			child.expect('$')
			#print('got ssh login')
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
	elif deviceAccess=='adb':
		child = winpexpect.winspawn('adb connect {}'.format(deviceIP))
		child.expect('connected to {}:5555'.format(deviceIP))
		print('adb connected')
	else:
		child=''
		print('ERROR: Please write deviceAccess label in lower case or appropriately')
	#findStationMAC(child)
	setHeaders(child)
	return child

# Only for customReport that requires extra exit. If it should have nothing, delete everything and write: pass
def exit(child):
	pass
	
def getCustomReport(child,i):
	iteration=int(i/originalLabelLength)
	i=i%originalLabelLength
	#print(iteration, i, originalLabelLength, len(CRValueName))
	devRadio=deviceRadio[iteration]
	s = 'adb -s 192.168.1.31 shell \"dumpsys wifi | grep \'mWifiInfo\'\"'
	#   adb -s 192.168.1.201 shell "dumpsys wifi | grep mWifiInfo"
	try:
		if deviceAccess=='adb':
			if i==0:
				#print("--------- TESTING ------------")
				child = winpexpect.winspawn('adb -s {} shell \"dumpsys wifi | grep \'mWifiInfo SSID\'\"'.format(deviceIP))
				child.expect('Frequency: ', timeout=10)
				child.expect('\d+')
				data = child.after
				#child.sendline('wl -i {} channel'.format(devRadio))
				#child.expect('current mac channel')
				#child.expect('\d+')
				#data = int(child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==1:
				child = winpexpect.winspawn('adb -s {} shell \"dumpsys wifi | grep \'mWifiInfo SSID\'\"'.format(deviceIP))
				child.expect('RSSI: ', timeout=10)
				child.expect('-\d\d')
				data = child.after
				# child.sendline('wl -i {} bssid'.format(devRadio))
				# child.expect('bssid')
				# child.expect('[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]')
				# data = (child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==2:
				child = winpexpect.winspawn('adb -s {} shell \"dumpsys wifi | grep \'mWifiInfo SSID\'\"'.format(deviceIP))
				child.expect('speed: ', timeout=10)
				child.expect('\d+')
				data = child.after
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==3:
				child = winpexpect.winspawn('adb -s {} shell \"dumpsys wifi | grep \'mWifiInfo SSID\'\"'.format(deviceIP))
				child.expect('BSSID: ', timeout=10)
				child.expect('[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]:[0-9a-fA-F][0-9a-fA-F]')
				data = child.after
				print ('{}: '.format(CRValueName[i]),data)
				return data
		elif deviceAccess=='ssh':
			if i==0:
				child.sendline('cd \/System\/Library\/PrivateFrameworks\/Apple80211.framework\/Versions\/Current\/Resources')
				child.expect('$')
				child.sendline('./airport -I') # was 'wl -i eth2 rssi'
				child.expect('channel:')
				child.expect('\d+')
				data = int(child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==1:
				child.sendline('./airport -I') # was 'wl -i eth2 rssi'
				child.expect('agrCtlRSSI:')
				child.expect('-\d\d|\d')
				data = int(child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data
			elif i==2:
				child.sendline('./airport -I') # was 'wl -i eth2 rssi'
				child.expect('lastTxRate:')
				child.expect('\d+')
				data = int(child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data			
			elif i==3:
				child.sendline('./airport -I') # was 'wl -i eth2 rssi'
				child.expect('MCS:')
				child.expect('\d+|-\d')
				data = int(child.after)
				print ('{}: '.format(CRValueName[i]),data)
				return data	
				
		return "#N/A"
	except:
		print("ERROR - Timeout reached")
		print("Error on child.before:", child.before,"& child.after:",child.after)
		data = "#ERROR"
		print ('{}: '.format(CRValueName[i]),data)
		return data


