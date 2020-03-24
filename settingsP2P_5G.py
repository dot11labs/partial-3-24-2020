import sys
import importlib
from datetime import datetime

#IP address of turn table
tt = '192.168.1.52'# .51 is loc 1F, .52 is Loc 2D# Client #1 as LEADER (Clockwise)
ttType='octoscope' #'dot11' or 'octoscope'
ttClient = ['192.168.1.54','192.168.1.50','192.168.1.55','192.168.1.53'] # Client #2, etc as FOLLOWERS (Clockwise)
ttClientType=['octoscope','octoscope','octoscope','octoscope']#[]
ttAP = ['192.168.1.51']#'192.168.1.53']# .53 is loc 1E, .55 is loc 1C# AP(s) as FOLLOWERS (Counter-clockwise)
ttAPType=['octoscope']

#Test description
testAP='Frontier_P2'
testAPSerial='Sagemcom F288 DB Ext'
testAPAnt='P2P DB-5G Downlink'
testAPFW='AF unknown'
testAPLoc='1S'
testSTA='Individual'
testSTASerial=''
testSTAFW=''
testSTAAnt=''
testSTALoc='5G-Near-Mid-Far'
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
trafficScript=['P2P_Downlink_Moto_X','P2P_Downlink_ac_laptop', 'P2P_Downlink_iPhone', 'P2P_Downlink_GS']
#trafficScript=['P2P_Downlink_ax_laptop', 'P2P_Downlink_MacBookPro']


#Throughput Software. If no customReport being use, please manually start iperf server from the client.
throughputSW='chariot' # 'iperf3' or 'chariot'
chariotPairsSummed=False # True / False

# iperf3 settings
iperf3Server='192.168.1.99'
throughputProtocol='tcp'
iperfUdpBandwidth='500M' # -u -b commands sent/automatically added
iperfOptions='-P 5' # Add TCP window size, number of parallel streams

# Throughput test settings
testDuration=20
trainingTime=5
dateAndTime=str(datetime.now().strftime("%m-%d-%Y_%I.%M%p"))
delay=7 # Compensate additional time to create graphs, actually finish the runtst test, deleting unecessary graphs files
#Windows RSSI Only work for 1 pair for now
enableWindowsRSSI=False
		
step=360
turntablePosition=0#initial/starting turntable position
testLength=1 # the amount of times the turntable rotate from 0 to 360

# Enabling custom report and specifying its values
# customReport #  1   ,  2,      3,      4,     5,      6,      7
#                MotoX ,88ax-N, 11ac-pc, GS10, 11ax-pc, 88ax-F, MBP
#customReport=[[ False, 	False,  False,  False,   True, False,   False],
#				[False, 	False,  False,  False,   False, False,   True]] # Value has to be: True/False
customReport= [[ True,  False,  False,  False,   False,  False,  False],  # moto x
			     [False, False,  True,   False,   False,  False,   False],  # 11ac laptop
			     [False, False,  False,  False,   False,  False,   False],   # iphone 8
			     [False, False,  False,  True,    False,  False,   False]    # GS10+
			  ]
  			     #[False, False,  False,  False,   True,   False,   False],     # 11ax laptop
				 #[False, False,  False,  False,   False,  False,   True]]  #MBP 
			    # Value has to be: True/False
			   
customReportTime=1 #testDuration/2
logInEveryStep=True # Cannot do this for iperf3 automation

cust=[]
for i in range(len(customReport[0])):
	cust.append(importlib.import_module("configFile.{}.customReport{}".format(testAP, (i+1))))
