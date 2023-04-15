#!/usr/bin/python3
import getopt
import os
import requests
import sys
import json
import time
from ftntlib import FortiManagerJSON
from tabulate import tabulate

def check(result):
    if result[0]['code'] != 0:
        raise TypeError(result[0]['message'] + ' (code='+ str(result[0]['code'])+')' )
    if not result[1][0]['response']['results'] :
        raise TypeError('not results')

#  Parameter 
hostname = ''
username = 'admin'
password = ''
adom = 'root'
firewall = ''
vdom = 'root'

# Variable
serial = ''
version = ''
build = ''

clr_bg_red = '\033[0;37;41m'
clr_bg_yellow = '\033[0;30;43m'
clr_fg_yellow = '\033[1;33;40m'
clr_fg_white = '\033[1;37;40m'
clr_fg_green = '\033[1;32;40m'
clr_fg_grey = '\033[1;30;40m'
clr_fg_red = '\033[1;31;40m'
clr_fg_purple = '\033[1;35;40m'
clr_fg_blue = '\033[1;34;40m'
clr_reset = '\033[0m'

if len(sys.argv) < 3:
	print ('monitor_fmg_sdwan.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>')
	exit()
try:
	opts, args = getopt.getopt(sys.argv[1:],'hi:u:p:a:f:v:')
except getopt.GetoptError:
		print ('monitor_fmg_sdwan.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>')
		sys.exit(2)
for opt, arg in opts:
	if opt in ('-h','--help'):
		print ('monitor_fmg_sdwan.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>')
		sys.exit()
	elif opt in ('-i'):
		hostname = arg
	elif opt in ('-u'):
		username = arg
	elif opt in ('-p'):
		password = str(arg)
	elif opt in ('-a'):
		adom = str(arg)
	elif opt in ('-f'):
		firewall = str(arg) 
	elif opt in ('-v'):
		vdom = str(arg) 

if hostname == '' or password == '' or firewall == '':
	print ('monitor_fmg_sdwan.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>')
	sys.exit()

fmg = FortiManagerJSON()
try:
    # fmg.debug('on')
    fmg.login(hostname, username, password)
    while True:
        data = {'target': 'adom/' + adom + '/device/' + firewall,  'resource' : "/api/v2/monitor/virtual-wan/members?vdom=" + vdom, 'action': "get"}
        url = "sys/proxy/json"
        result = fmg.execute(url,data)
        check(result)
        data_result = result[1]
        members = data_result[0]['response']

        data = {'target': 'adom/' + adom + '/device/' + firewall,  'resource' : "/api/v2/monitor/virtual-wan/health-check?vdom=" + vdom, 'action': "get"}
        url = "sys/proxy/json"
        result = fmg.execute(url,data)
        check(result)
        data_result = result[1]
        hc = data_result[0]['response']


        serial = members['serial']
        version = members['version']
        build = members['build']

        os.system('clear')
        table = []
        print ('%sTime : %s\033[0m  %sDevice: %s (%s) Version %s build%s\n' % (clr_bg_red, time.ctime(), clr_bg_yellow, firewall, serial, version, build))
        print (clr_bg_yellow + "SD-WAN members")
        headers = [clr_fg_blue + 'name', 'link', 'session', 'tx_bandwidth(bps)', 'rx_bandwidth(bps)', 'tx_bytes', 'rx_bytes']
        for interface in members['results'].keys():
            if members['results'][interface]['link'] != "down":
                color_l = clr_fg_green
            else:
                color_l = clr_fg_red
            
            table.append([
                clr_fg_yellow + interface,
                color_l + members['results'][interface]['link'],
                clr_fg_white + str(members['results'][interface]['session']),
                clr_fg_white + str(members['results'][interface]['tx_bandwidth']),
                clr_fg_white + str(members['results'][interface]['rx_bandwidth']),
                clr_fg_white + str(members['results'][interface]['tx_bytes']),
                clr_fg_white + str(members['results'][interface]['rx_bytes'])
            ])

            if 'child_intfs' in members['results'][interface]:
                for child in members['results'][interface]['child_intfs'].keys():
                    if members['results'][interface]['child_intfs'][child]['link'] != 'down':
                        color_l = clr_fg_green
                        # print (members['results'][interface]['child_intfs'][child]['link'])
                    else:
                        color_l = clr_fg_red
                    table.append([
                        clr_fg_yellow + child,
                        color_l + members['results'][interface]['child_intfs'][child]['link'],
                        clr_fg_white + str(members['results'][interface]['child_intfs'][child]['session']),
                        clr_fg_white + str(members['results'][interface]['child_intfs'][child]['tx_bandwidth']),
                        clr_fg_white + str(members['results'][interface]['child_intfs'][child]['rx_bandwidth']),
                        clr_fg_white + str(members['results'][interface]['child_intfs'][child]['tx_bytes']),
                        clr_fg_white + str(members['results'][interface]['child_intfs'][child]['rx_bytes'])
                    ])
       
        print(tabulate(table, headers, numalign="right"))

        for health in hc['results'].keys():
            print (clr_bg_yellow + "\nSD-WAN health-check: " + health)
            table = []
            headers = [clr_fg_blue + "name","status","sla_targets_met", "latency","jitter","packet_loss","packet_sent","packet_received","session","tx_bandwidth","rx_bandwidth"]
            for port in hc['results'][health].keys():
                if hc['results'][health][port]['status'] == "error":
                    pass
                elif hc['results'][health][port]['status'] == "down":
                    table.append([
                        clr_fg_yellow + port,
                        clr_fg_red + hc['results'][health][port]['status'] ])    
                else :
                    if hc['results'][health][port]['packet_loss'] == 0:
                        color_p = clr_fg_white
                    else: 
                        color_p = clr_fg_red
                    
                    table.append([
                        clr_fg_yellow + port,
                        clr_fg_green + hc['results'][health][port]['status'],
                        clr_fg_white + str(hc['results'][health][port]['sla_targets_met']),
                        clr_fg_white + str(round(hc['results'][health][port]['latency'],3)),
                        clr_fg_white + str(round(hc['results'][health][port]['jitter'],3)),
                        color_p + str(hc['results'][health][port]['packet_loss']) ,
                        clr_fg_white + str(hc['results'][health][port]['packet_sent']),
                        clr_fg_white + str(hc['results'][health][port]['packet_received']),
                        clr_fg_white + str(hc['results'][health][port]['session']),
                        clr_fg_white + str(hc['results'][health][port]['tx_bandwidth']),
                        clr_fg_white + str(hc['results'][health][port]['rx_bandwidth'])
                    ])
            print(tabulate(table, headers, numalign="right"))
        time.sleep(2)
                
    
    # fmg.debug('off')

except TypeError as identifier : 
    print ('%sError: %s%s' % (clr_bg_red, identifier, clr_reset))

except KeyError as identifier:
	print ('%sInvalid data format%s' % (clr_bg_red, clr_reset))
	
except KeyboardInterrupt :
    print ('%sInterrupt by user %s' % (clr_bg_yellow, clr_reset))

except (requests.exceptions.ConnectionError, OSError):
    print('%sFailed to establish a connection to %s%s' % (clr_bg_red, hostname, clr_reset))

except json.decoder.JSONDecodeError: 
	print ('%sLogin failed to %s%s' % (clr_bg_red, hostname, clr_reset))

finally:
    fmg.logout()
    # fmg.debug('off')
    print("Exit")
