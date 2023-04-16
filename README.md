# Monitor_ftnt 
#### v1.0.0 (April, 14, 2023)
#### Script Python for Fortinet device monitoring

## monitor_fos_sdwan
Monitoring parameter SD-WAN of a FortiGate in realtime.  
Show SD-WAN members, traffic and health-chek status every 2 seconds.

Usage:

`monitor_fos_sdwan.py  -i <ipaddress> -u <username> -p <password>`
> `<ipaddress>` Firewall IP address     
> `<username>` Firewall Admin username (default=*admin*)      
> `<password>` Firewall Admin password 


## monitor_fos_ts  
Monitoring traffic shaping of a FortiGate in realtime.  
Show the class_id for each interface and its values: allocated_bandwidth, max_bandwidth, guaranteed_bandwidth, priority, current_bandwidth, drop_bytes, forwarded_bytes.  

Usage:

`monitor_fos_ts.py -i <ipaddress> -u <username> -p <password>`
> `<ipaddress>` Firewall IP address     
> `<username>` Firewall Admin username (default=*admin*)     
> `<password>` Firewall Admin password 

## monitor_fmg_sdwan  
Monitoring parameter SD-WAN of a FortiGate in realtime from FortiManger.   
Show SD-WAN members, traffic and health-chek status every 2 seconds.  

Usage:

`monitor_fmg_sdwan.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>`
> `<ipaddress>` FMG IP address     
> `<username>` FMG Admin username (default=*admin*)      
> `<password>` FMG Admin password         
> `<adom>` Adom (default=*root*)         
> `<device>` Device name (firewall hostname)  
> `<vdom>` Device VDOM (default=*root*)

## monitor_fmg_ts
Monitoring traffic shaping of a FortiGate in realtime from FortiManger.  
Show the class_id for each interface and its values: allocated_bandwidth, max_bandwidth, guaranteed_bandwidth, priority, current_bandwidth, drop_bytes, forwarded_bytes.  

Usage:

`monitor_fmg_ts.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>`
> `<ipaddress>` FMG IP address     
> `<username>` FMG Admin username (default=*admin*)      
> `<password>` FMG Admin password         
> `<adom>` Adom (default=*root*)         
> `<device>` Device name (firewall hostname)  
> `<vdom>` Device VDOM (default=*root*)

## Prerequisities  
- Python 3.9.6+ with this packages:
    - requests (https://pypi.org/project/setuptools/)
    - lxml (https://pypi.org/project/lxml/)
    - setuptools (https://pypi.org/project/setuptools/)
    - suds (https://pypi.org/project/suds/)
    - tabulate (https://pypi.org/project/tabulate/)
- FTNTLIB Python Module 0.4.0.dev18 (https://fndn.fortinet.net/index.php?/tools/file/4-ftntlib-python-module/)


