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

if len(sys.argv) < 3:
    print('monitor_fmg_ts.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>')
    exit()
try:
    opts, args = getopt.getopt(sys.argv[1:], 'hi:u:p:a:f:v:')
except getopt.GetoptError:
    print('monitor_fmg_ts.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>')
    sys.exit(2)
for opt, arg in opts:
    if opt in ('-h', '--help'):
        print('monitor_fmg_ts.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>')
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
    print('monitor_fmg_ts.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>')
    sys.exit()

fmg = FortiManagerJSON()
try:
    # fmg.debug('on')
    fmg.login(hostname, username, password)
    while True:
        data = {'target': 'adom/' + adom + '/device/' + firewall,
                'resource': "/api/v2/monitor/firewall/shaper/multi-class-shaper?vdom=" + vdom, 'action': "get"}
        url = "sys/proxy/json"
        result = fmg.execute(url, data)
        check(result)
        data_result = result[1]
        shaper = data_result[0]['response']

        serial = shaper['serial']
        version = shaper['version']
        build = shaper['build']
        os.system('clear')
        print('%sTime : %s\033[0m  %sDevice: %s (%s) Version %s build%s\n' % (
            clr_bg_red, time.ctime(), clr_bg_yellow, firewall, serial, version, build))

        for classes in shaper['results']:
            interface = classes['interface']
            bandwidth = classes['bandwidth']
            default_class = classes['default_class']
            if 'parent' in classes.keys() and 'peer_id' in classes.keys() and 'remote_gateway' in classes.keys() :
                parent = classes['parent']
                peer_id = classes['peer_id']
                remote_gateway = classes['remote_gateway']
                print('\n%sInterface: %s bandwidth: %s  default class_id: %s\033[0m  %sParent: %s Peer: %s Remote gateway: %s%s' % (
                    clr_bg_yellow, interface, bandwidth, default_class, clr_bg_green, parent, peer_id, remote_gateway, clr_fg_blue))
            else:
                print('\n%sInterface: %s bandwidth: %s  default class_id: %s%s' % (
                    clr_bg_yellow, interface, bandwidth, default_class, clr_fg_blue))
            # print (clr_fg_blue + 'id   name         allocated_bandwidth    max_bandwidth    guaranteed_bandwidth    priority    current_bandwidth    drop_bytes    forwarded_bytes')
            headers = [clr_fg_blue + 'id', 'name', 'allocated_bandwidth', 'max_bandwidth',
                       'guaranteed_bandwidth', 'priority', 'current_bandwidth', 'drop_bytes', 'forwarded_bytes']
            table = []
            for active_classes in classes['active_classes']:
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

    # fmg.debug('off')

except TypeError as identifier:
    print ('%sError: %s%s' % (clr_bg_red, identifier, clr_reset))

except KeyError as identifier:
    print('%sInvalid data format%s' % (clr_bg_red, clr_reset))

except KeyboardInterrupt:
    print('%sInterrupt by user %s' % (clr_bg_yellow, clr_reset))

except (requests.exceptions.ConnectionError, OSError):
    print('%sFailed to establish a connection to %s%s' %
          (clr_bg_red, hostname, clr_reset))

except json.decoder.JSONDecodeError:
    print('%sLogin failed to %s%s' % (clr_bg_red, hostname, clr_reset))

finally:
    fmg.logout()
    # fmg.debug('off')
    print("Exit")
