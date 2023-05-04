# Monitor_ftnt 
#### Script Python for Fortinet device monitoring

## **Install the Python scripts**
To install the scripts in your machine, follow one of two way.
### 1) Git command
Run the following commands in your shell to install the scripts from GitHub:
```console
$ git clone https://github.com/nidica/monitor_ftnt.git
$ cd monitor_ftnt
```
### 2) Download the package 
 Downaload the file (*.zip* or *.tar.gz*) in [latest release](https://github.com/nidica/monitor_ftnt/releases) from GitHub.  
 Extract the files in a directory and run the scripts.  

## **Usage**
## monitor_fos_sdwan
Monitoring parameter SD-WAN of a FortiGate in realtime.  
Show SD-WAN members, traffic and health-chek status every 2 seconds.

Usage:

```console
./monitor_fos_sdwan.py  -i <ipaddress> -u <username> -p <password>
```
> `<ipaddress>` Firewall IP address     
> `<username>` Firewall Admin username (default=*admin*)      
> `<password>` Firewall Admin password 

![monitor_fos_sdwan](/image/monitor_fos_sdwan.png "monitor_fos_sdwan")

## monitor_fos_ts  
Monitoring traffic shaping of a FortiGate in realtime.  
Show the class_id for each interface and its values: allocated_bandwidth, max_bandwidth, guaranteed_bandwidth, priority, current_bandwidth, drop_bytes, forwarded_bytes.  

Usage:

```console
./monitor_fos_ts.py -i <ipaddress> -u <username> -p <password>
```  
> `<ipaddress>` Firewall IP address     
> `<username>` Firewall Admin username (default=*admin*)     
> `<password>` Firewall Admin password 

![monitor_fos_ts](/image/monitor_fos_ts.png "monitor_fos_ts")


## monitor_fmg_sdwan  
Monitoring parameter SD-WAN of a FortiGate in realtime from FortiManger.   
Show SD-WAN members, traffic and health-chek status every 2 seconds.  

Usage:

```console
./monitor_fmg_sdwan.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>  
```
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

```console
./monitor_fmg_ts.py -i <ip_fmg> -u <username> -p <password> -a <adom> -f <device> -v <vdom>
```
> `<ipaddress>` FMG IP address     
> `<username>` FMG Admin username (default=*admin*)      
> `<password>` FMG Admin password         
> `<adom>` Adom (default=*root*)         
> `<device>` Device name (firewall hostname)  
> `<vdom>` Device VDOM (default=*root*)

## **Pre-requisites**  
- Python 3.9.6+ with this packages:
    - requests (https://pypi.org/project/requests/)
    - setuptools (https://pypi.org/project/setuptools/): Easily download, build, install, upgrade, and uninstall Python packages
    - tabulate (https://pypi.org/project/tabulate/): Pretty-print tabular data
    - pyFMG (https://pypi.org/project/pyfmg/): Represents the base components of the Fortinet FortiManager JSON-RPC interface
    - pyFGT (https://pypi.org/project/pyfgt/): Represents the base components of the Fortinet FortiGate REST interface with abstractions

Notice: all the scripts use the python3 interpeter in */usr/bin/* directory. Please, change the path if your python3 is in other one.

## **Run scripts in Docker container**
Another way to run the scripts is to download a docker image in your machine.  
[Download](https://hub.docker.com/r/ndicaprio/mnt_ftnt) the image from docker hub and follow the instructions.