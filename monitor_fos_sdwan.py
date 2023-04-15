#!/usr/bin/python3
import os
import sys
import getopt
import json
from ftntlib import FortiOSREST
import time
import requests
from tabulate import tabulate

#  Parameter 
hostname = ''
username = 'admin'
password = ''
#  Variable 
serial = ''
version = ''
build = ''
clr_fg_gray_n = '\033[0;37;40m'
clr_bg_red = '\033[0;37;41m'
clr_bg_blu = '\033[0;37;44m'
clr_bg_yellow = '\033[0;30;43m'
clr_fg_yellow_n = '\033[0;33;40m'
clr_fg_yellow = '\033[1;33;40m'
clr_fg_white = '\033[1;37;40m'
clr_fg_green = '\033[1;32;40m'
clr_fg_grey = '\033[1;30;40m'
clr_fg_red = '\033[1;31;40m'
clr_fg_purple = '\033[1;35;40m'
clr_fg_purple_n = '\033[0;35;40m'
clr_fg_blue = '\033[1;34;40m'
clr_reset = '\033[0m'


if len(sys.argv) < 2:
	print ('monitor_fos_sdwan.py -i <ipaddress> -u <username> -p <password>')
	sys.exit(2)
try:
	opts, args = getopt.getopt(sys.argv[1:],'hi:u:p:')
except getopt.GetoptError:
		print ('monitor_fos_sdwan.py -i <ipaddress> -u <username> -p <password>')
		sys.exit(2)
for opt, arg in opts:
	if opt in ('-h','--help'):
		print ('monitor_fos_sdwan.py -i <ipaddress> -u <username> -p <password>')
		sys.exit()
	elif opt in ('-i'):
		hostname = arg
	elif opt in ('-u'):
		username = arg
	elif opt in ('-p'):
		password = str(arg)

if hostname == '' or password == '':
	print ('monitor_fos_sdwan.py -i <ipaddress> -u <username> -p <password>')
	sys.exit()

fgt = FortiOSREST()    
try:
	#fgt.debug('on')    
	fgt.login(hostname, username, password)
	cmdb_sdwan = fgt.get('cmdb', 'system', 'sdwan')
	sdwan = json.loads(cmdb_sdwan)
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

	# raise TypeError('exit')
	while True:  
		data = fgt.get('monitor', 'virtual-wan', 'members')
		members = json.loads(data)
		data1 = fgt.get('monitor', 'virtual-wan', 'health-check')
		members1 = json.loads(data1)

		serial = members['serial']
		version = members['version']
		build = members['build']
		os.system('clear')
		table = []
		table_members =[]
		print ('%sTime : %s\033[0m  %sHostname: %s (%s) Version %s build%s\n' % (clr_bg_red, time.ctime(), clr_bg_yellow, hostname, serial, version, build))
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
		
		print (clr_bg_yellow + "\nSD-WAN traffic")
		# headers = [clr_fg_blue + 'name', 'link', 'session', 'tx_bandwidth(bps)', 'rx_bandwidth(bps)', 'tx_bytes', 'rx_bytes']
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

		for health in members1['results'].keys():
			print (clr_bg_yellow + "\nSD-WAN health-check: " + health, end=' ')
			if health_check[health]['detect-mode'] != 'remote':
				print (clr_bg_blu + ' Server:', health_check[health]['server'], '- Protocol:', health_check[health]['protocol'] )
			else:
				print (clr_bg_blu + ' Detect Mode: Remote - Protocol:', health_check[health]['protocol'] )

			table = []
			headers = [clr_fg_blue + "name","status","sla_targets_met", "latency","jitter","packet_loss","packet_sent","packet_received","session","tx_bandwidth","rx_bandwidth"]
			for port in members1['results'][health].keys():
				if members1['results'][health][port]['status'] == "error":
					pass
				elif members1['results'][health][port]['status'] == "down":
					table.append([
                        clr_fg_yellow + port,
                        clr_fg_red + members1['results'][health][port]['status'] ])    
				else :
					if members1['results'][health][port]['packet_loss'] == 0:
						color_p = clr_fg_white
					else: 
						color_p = clr_fg_red

					table.append([
                        clr_fg_yellow + port,
                        clr_fg_green + members1['results'][health][port]['status'],
                        clr_fg_white + str(members1['results'][health][port]['sla_targets_met']),
                        clr_fg_white + str(round(members1['results'][health][port]['latency'],3)),
                        clr_fg_white + str(round(members1['results'][health][port]['jitter'],3)),
                        color_p + str(members1['results'][health][port]['packet_loss']) ,
                        clr_fg_white + str(members1['results'][health][port]['packet_sent']),
                        clr_fg_white + str(members1['results'][health][port]['packet_received']),
                        clr_fg_white + str(members1['results'][health][port]['session']),
                        clr_fg_white + str(members1['results'][health][port]['tx_bandwidth']),
                        clr_fg_white + str(members1['results'][health][port]['rx_bandwidth'])
                    ])

					if 'child_intfs' in members1['results'][health][port]:
						for child in members1['results'][health][port]['child_intfs'].keys():
							if members1['results'][health][port]['child_intfs'][child]['packet_loss'] == 0:
								color_p = clr_fg_white
							else: 
								color_p = clr_fg_red
							table.append([
								clr_fg_yellow + child,
								clr_fg_green + members1['results'][health][port]['status'],
                        		clr_fg_white + str(members1['results'][health][port]['child_intfs'][child]['sla_targets_met']),
                        		clr_fg_white + str(round(members1['results'][health][port]['child_intfs'][child]['latency'],3)),
								clr_fg_white + str(round(members1['results'][health][port]['child_intfs'][child]['jitter'],3)),
								color_p + str(members1['results'][health][port]['child_intfs'][child]['packet_loss']) ,
								clr_fg_white + str(members1['results'][health][port]['child_intfs'][child]['packet_sent']),
								clr_fg_white + str(members1['results'][health][port]['child_intfs'][child]['packet_received']),
								clr_fg_white + str(members1['results'][health][port]['child_intfs'][child]['session']),
								clr_fg_white + str(members1['results'][health][port]['child_intfs'][child]['tx_bandwidth']),
								clr_fg_white + str(members1['results'][health][port]['child_intfs'][child]['rx_bandwidth'])
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

except TypeError as identifier:
    print ('%sError: %s%s' % (clr_bg_red, identifier, clr_reset))
    
except KeyboardInterrupt:
	print ('%sMonitor sd-wan to %s terminated%s' % (clr_bg_red, hostname, clr_reset))

except KeyError:
	print ('%sInvalid data format %s' % (clr_bg_red, clr_reset))
	
except json.decoder.JSONDecodeError: 
	print ('%sLogin failed to %s%s' % (clr_bg_red, hostname, clr_reset))

except (requests.exceptions.ConnectionError, OSError):
	print('%sFailed to establish a connection to %s%s' % (clr_bg_red, hostname, clr_reset))

finally:
	#print 'Finally close client'
	fgt.logout()
	print("Exit")
	
	