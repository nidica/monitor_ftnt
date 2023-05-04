#!/usr/bin/python3
import getopt
import os
import string
import sys
import time
import requests
from pyFGT import fortigate
from tabulate import tabulate

def check(data):
    if data[1]['status'] != 'success':
        raise TypeError('Status error from the request')
    if not data[1]['results'] :
        raise TypeError('No results from the request')
    
#  Parameter 
ipfirewall = ''
username = 'admin'
password = ''
#  Variable 
serial = ''
version = ''
build = ''
clr_bg_red = '\033[0;37;41m'
clr_bg_green = '\033[0;30;42m'
clr_bg_yellow = '\033[0;30;43m'
clr_fg_yellow = '\033[1;33;40m'
clr_fg_white = '\033[1;37;40m'
clr_fg_green = '\033[1;32;40m'
clr_fg_grey = '\033[1;30;40m'
clr_fg_red = '\033[1;31;40m'
clr_fg_purple = '\033[1;35;40m'
clr_fg_blue = '\033[1;34;40m'
clr_reset = '\033[0m'


if len(sys.argv) < 2:
	print ('monitor_fos_ts.py -i <ipaddress> -u <username> -p <password>')
	sys.exit(2)
try:
	opts, args = getopt.getopt(sys.argv[1:],'hi:u:p:')
except getopt.GetoptError:
		print ('monitor_fos_ts.py -i <ipaddress> -u <username> -p <password>')
		sys.exit(2)
for opt, arg in opts:
	if opt in ('-h','--help'):
		print ('monitor_fos_ts.py -i <ipaddress> -u <username> -p <password>')
		sys.exit()
	elif opt in ('-i'):
		ipfirewall = arg
	elif opt in ('-u'):
		username = arg
	elif opt in ('-p'):
		password = str(arg)

if ipfirewall == '' or password == '':
	print ('monitor_fos_sdwan.py -i <ipaddress> -u <username> -p <password>')
	sys.exit()

fgt_istance = fortigate.FortiGate(ipfirewall, username, password, debug=False, disable_request_warnings=True)

try:
	fgt_istance.login()
	status = fgt_istance.get('/monitor/system/status')
	check(status)
	hostname = status[1]['results']['hostname']
	model = status[1]['results']['model']
	model_number = status[1]['results']['model_number']
	model_name = status[1]['results']['model_name']
		
	while True:  
		shaper = fgt_istance.get('/monitor/firewall/shaper/multi-class-shaper')
		check(shaper)
		serial = shaper[1]['serial']
		version = shaper[1]['version']
		build = shaper[1]['build']
		os.system('clear')
		print ('%sTime : %s\033[0m  %sHostname: %s (%s) IP: %s Version %s build%s' % (clr_bg_red, time.ctime(), clr_bg_yellow, hostname , serial, ipfirewall, version, build))
		for results in shaper[1]['results']:
			interface = results['interface']
			bandwidth = results['bandwidth']
			default_class = results['default_class']
			if 'parent' in results.keys() and 'peer_id' in results.keys() and 'remote_gateway' in results.keys() :
				parent = results['parent']
				peer_id = results['peer_id']
				remote_gateway = results['remote_gateway']
				print('\n%sInterface: %s bandwidth: %s  default class_id: %s\033[0m  %sParent: %s Peer: %s Remote gateway: %s%s' % (
                    clr_bg_yellow, interface, bandwidth, default_class, clr_bg_green, parent, peer_id, remote_gateway, clr_fg_blue))
			else:
				print ('\n%sInterface: %s bandwidth: %s  default class_id: %s%s' % (clr_bg_yellow, interface, bandwidth, default_class, clr_fg_blue) )
			headers = [clr_fg_blue + 'id','name','allocated_bandwidth','max_bandwidth','guaranteed_bandwidth','priority','current_bandwidth','drop_bytes','forwarded_bytes']
			table = []
			for active_classes in results['active_classes']:
				if active_classes['current_bandwidth'] != 0:
					color_cb = clr_fg_green
				else:
					color_cb = clr_fg_grey
				table.append([
					clr_fg_yellow + str(active_classes['class_id']),
					clr_fg_yellow + active_classes['class_name'],
					clr_fg_white + str(active_classes['allocated_bandwidth']),
                    clr_fg_white + str(active_classes['max_bandwidth']),
					clr_fg_white + str(active_classes['guaranteed_bandwidth']),
					clr_fg_white + str(active_classes['priority']),
                    color_cb + str(active_classes['current_bandwidth']),
                    clr_fg_red + str(active_classes['dropped_bytes']),
                    clr_fg_purple + str(active_classes['forwarded_bytes'])
				])
				
			print(tabulate(table, headers, numalign="right"))

		time.sleep(2)
		# fgt_istance.logout()

except fortigate.FGTValidSessionException as identifier:
    print ('%sError: %s%s' % (clr_bg_red, identifier, clr_reset))

except fortigate.FGTBaseException as identifier:
	print ('%sError: %s%s' % (clr_bg_red, identifier, clr_reset))

except TypeError as identifier:
    print ('%sError: %s%s' % (clr_bg_red, identifier, clr_reset))
    
except KeyboardInterrupt:
	print ('%sInterrupt by user %s' % (clr_bg_yellow, clr_reset))
	
except (requests.exceptions.ConnectionError, OSError):
	print ('%sFailed to establish a connection to %s%s' % (clr_bg_red, ipfirewall, clr_reset))

finally:
	# fgt_istance.logout()
	print("Exit")
	
	