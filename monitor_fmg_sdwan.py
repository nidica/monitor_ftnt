#!/usr/bin/python3
import getopt
import os
import requests
import sys
import json
import time
from pyFMG import fortimgr
from tabulate import tabulate

def check(result):
    if result[0] != 0:
        raise TypeError('Status Code=' + str(result[1]['status']['code']) + '  Message=' + str(result[1]['status']['message']))
    
    if result[1][0]['status']['code'] !=0 :
        raise TypeError('Status Code=' + str(result[1][0]['status']['code']) + '  Message=' + str(result[1][0]['status']['message']))

    if 'response' in  result[1][0]:
         if not result[1][0]['response']['results'] :
            raise TypeError('No results from the request')

def check_get(result):
    if result[0] != 0:
        raise TypeError('Status Code=' + str(result[1]['status']['code']) + '  Message=' + str(result[1]['status']['message']))

#  Parameter 
ip_fmg = ''
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
clr_bg_blu = '\033[0;37;44m'
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
		ip_fmg = arg
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

if ip_fmg == '' or password == '' or firewall == '':
	print ('monitor_fmg_sdwan.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>')
	sys.exit()

fmg = fortimgr.FortiManager(ip_fmg, username, password, debug=False, disable_request_warnings=True)

try:
    fmg.login()
    url = 'dvmdb/adom/{0}/device/{1}'.format(adom, firewall)
    device = fmg.get(url)
    check_get(device)
    ip_firewall = device[1]['ip']

    data = {'target': 'adom/' + adom + '/device/' + firewall,  'resource' : "/api/v2/cmdb/system/sdwan?vdom=" + vdom, 'action': "get"}
    url = "sys/proxy/json"
    result = fmg.execute(url,data=data)
    check(result)
    data_result = result[1]
    sdwan = data_result[0]['response']
    if sdwan['results']['status'] == 'disable':
          raise TypeError('SD-WAN disable')

    zone_sdwan = {}
    for members in sdwan['results']['members']:
        zone_sdwan[members['interface']] = {
            'seq-num': members['seq-num'],
            "zone": members['zone'],
            "gateway": members['gateway'],
            "source": members['source'],
            "cost": members['cost'],
            "weight": members['weight'],
            "priority": members['priority']
        }

    health_check = {}
    for hc in sdwan['results']['health-check']:
        health_check[hc['name']] = {
            'server': hc['server'],
            'protocol': hc['protocol'],
            'detect-mode': hc['detect-mode'],
            'sla': hc['sla']
        }
    
    while True:
        data = {'target': 'adom/' + adom + '/device/' + firewall,  'resource' : "/api/v2/monitor/virtual-wan/members?vdom=" + vdom, 'action': "get"}
        url = "sys/proxy/json"
        result = fmg.execute(url,data=data)
        check(result)
        data_result = result[1]
        members = data_result[0]['response']

        data = {'target': 'adom/' + adom + '/device/' + firewall,  'resource' : "/api/v2/monitor/virtual-wan/health-check?vdom=" + vdom, 'action': "get"}
        url = "sys/proxy/json"
        result = fmg.execute(url,data=data)
        check(result)
        data_result = result[1]
        hc = data_result[0]['response']

        serial = members['serial']
        version = members['version']
        build = members['build']

        os.system('clear')
        table = []
        table_members =[]
        print ('%sTime : %s\033[0m  %sDevice: %s (%s) IP: %s Version %s build%s\n' % (clr_bg_red, time.ctime(), clr_bg_yellow, firewall, serial, ip_firewall, version, build))
        
        #******************
        #* SD-WAN members #
        #******************
        print (clr_bg_yellow + "SD-WAN members")
        headers_member = [clr_fg_blue + 'name', 'seq', 'zone', 'gateway', 'source', 'cost', 'weight', 'priority']
        for members_sdwan in zone_sdwan.keys():
            table_members.append([
				clr_fg_yellow + members_sdwan,
				clr_fg_white + str(zone_sdwan[members_sdwan]['seq-num']),
				clr_fg_purple + str(zone_sdwan[members_sdwan]['zone']),
				clr_fg_white + str(zone_sdwan[members_sdwan]['gateway']),
				clr_fg_white + str(zone_sdwan[members_sdwan]['source']),
				clr_fg_white + str(zone_sdwan[members_sdwan]['cost']),
				clr_fg_white + str(zone_sdwan[members_sdwan]['weight']),
				clr_fg_white + str(zone_sdwan[members_sdwan]['priority'])
			])
        print(tabulate(table_members, headers_member, numalign="right"))	
        
        #******************
        #* SD-WAN traffic #
        #******************
        print (clr_bg_yellow + "\nSD-WAN traffic")
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
        
        #***********************
        #* SD-WAN health-check #
        #***********************
        
        for health in hc['results'].keys():
            print (clr_bg_yellow + "\nSD-WAN health-check: " + health, end=' ')
            if health_check[health]['detect-mode'] != 'remote':
                print (clr_bg_blu + ' Server:', health_check[health]['server'], '- Protocol:', health_check[health]['protocol'] )
            else:
                print (clr_bg_blu + ' Detect Mode: Remote - Protocol:', health_check[health]['protocol'] )

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

                    if 'child_intfs' in hc['results'][health][port]:
                        for child in hc['results'][health][port]['child_intfs'].keys():
                            if hc['results'][health][port]['child_intfs'][child]['packet_loss'] == 0:
                                color_p = clr_fg_white
                            else: 
                                color_p = clr_fg_red
                            table.append([
                                clr_fg_yellow + child,
                                clr_fg_green + hc['results'][health][port]['status'],
                                clr_fg_white + str(hc['results'][health][port]['child_intfs'][child]['sla_targets_met']),
                                clr_fg_white + str(round(hc['results'][health][port]['child_intfs'][child]['latency'],3)),
                                clr_fg_white + str(round(hc['results'][health][port]['child_intfs'][child]['jitter'],3)),
                                color_p + str(hc['results'][health][port]['child_intfs'][child]['packet_loss']) ,
                                clr_fg_white + str(hc['results'][health][port]['child_intfs'][child]['packet_sent']),
                                clr_fg_white + str(hc['results'][health][port]['child_intfs'][child]['packet_received']),
                                clr_fg_white + str(hc['results'][health][port]['child_intfs'][child]['session']),
                                clr_fg_white + str(hc['results'][health][port]['child_intfs'][child]['tx_bandwidth']),
                                clr_fg_white + str(hc['results'][health][port]['child_intfs'][child]['rx_bandwidth'])
                            ])

            print(tabulate(table, headers, numalign="right"))
            print()			
            for sla in health_check[health]['sla']:
                print(clr_bg_blu + 'sla id:', sla['id'], '-', end=' ')
                if 'latency' in sla['link-cost-factor']: 
                    print ('latency=', sla['latency-threshold'], end=' ')
                if 'jitter' in sla['link-cost-factor']: 
                    print ('jitter=', sla['jitter-threshold'], end=' ')
                if 'packet-loss' in sla['link-cost-factor']: 
                    print ('packet-loss=', sla['packetloss-threshold'], end=' ')
                print(clr_reset)
				
        time.sleep(2)

except fortimgr.FMGValidSessionException as identifier:
    print ('%sValid Session Exception: FortiManager instance that had no valid session or was not connected.%s' % (clr_bg_red, clr_reset))

except fortimgr.FMGBaseException as identifier:
	print ('%sBase Exception: %s%s' % (clr_bg_red, identifier, clr_reset))

except fortimgr.FMGConnectTimeout as identifier:
	print ('%sConnect Timeout: %s%s' % (clr_bg_red, identifier, clr_reset))

except TypeError as identifier:
    print ('%sError: %s%s' % (clr_bg_red, identifier, clr_reset))
    
except KeyboardInterrupt:
	print ('%sInterrupt by user %s' % (clr_bg_yellow, clr_reset))
	
except json.decoder.JSONDecodeError: 
	print ('%sLogin failed to %s%s' % (clr_bg_red, ip_fmg, clr_reset))

except (requests.exceptions.ConnectionError, OSError):
	print ('%sFailed to establish a connection to %s%s' % (clr_bg_red, ip_fmg, clr_reset))

finally:
    fmg.logout()
    print("Exit")
