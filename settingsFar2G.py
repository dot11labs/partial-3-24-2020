import sys
import importlib
from datetime import datetime

#IP address of turn table
tt = '192.168.1.55'# .51 is loc 1F, .52 is Loc 2D# Client #1 as LEADER (Clockwise)
ttType='octoscope' #'dot11' or 'octoscope'
ttClient = [] # Client #2, etc as FOLLOWERS (Clockwise)
ttClientType=['octoscope']#[]
ttAP = ['192.168.1.50']#'192.168.1.53']# .53 is loc 1E, .55 is loc 1C# AP(s) as FOLLOWERS (Counter-clockwise)
ttAPType=['octoscope']

#Test description
testAP='Frontier_P2'
testAPSerial='ActionTec F3131V'
testAPAnt='Far2G'
testAPFW='no interference'
testAPLoc='1S'
testSTA='RT-AX88U'
testSTASerial=''
testSTAFW='3.0.0.4.384_6210'
testSTAAnt='2V2H'
testSTALoc='1A'
testName=testAP
testStardustName=''
if testAPSerial!='':
	testName+='_'+testAPSerial
if testSTA!='':
	testName+='_'+testSTA
if testAPAnt!='':
	testName+='_'+testAPAnt
if testAPAnt!='':
	testName+='_'+testAPLoc
if testAPAnt!='':
	testName+='_'+testSTALoc
	
# Traffic script ( *.tst files )
# For iperf3's testing, need to define 'Downlink' or/and 'Uplink'
# For ixChariot's testing, the trafficScript name needs to match the .tst file name
trafficScript=['Far2GUplink']

#Throughput Software. If no customReport being use, please manually start iperf server from the client.
throughputSW='chariot' # 'iperf3' or 'chariot'
chariotPairsSummed=True # True / False

# iperf3 settings
iperf3Server='192.168.1.99'
throughputProtocol='tcp'
iperfUdpBandwidth='500M' # -u -b commands sent/automatically added
iperfOptions='-P 5' # Add TCP window size, number of parallel streams

# Throughput test settings
testDuration=60
trainingTime=15
dateAndTime=str(datetime.now().strftime("%m-%d-%Y_%I.%M%p"))
delay=7 # Compensate additional time to create graphs, actually finish the runtst test, deleting unecessary graphs files
#Windows RSSI Only work for 1 pair for now
enableWindowsRSSI=False
		
step=10
turntablePosition=170#initial/starting turntable position
testLength=1 # the amount of times the turntable rotate from 0 to 360

# Enabling custom report and specifying its values
# customReport #  1   ,  2,      3,      4,     5,      6,      7
#                 AP ,STA N2, STA N5,  STA M2, STA M5, STA F2, STA F5
customReport=[[ False, 	False,  False,  False,  False,  True,  False]] # Value has to be: True/False
customReportTime=trainingTime/2#testDuration/2
logInEveryStep=True # Cannot do this for iperf3 automation

cust=[]
for i in range(len(customReport[0])):
	cust.append(importlib.import_module("configFile.{}.customReport{}".format(testAP, (i+1))))
