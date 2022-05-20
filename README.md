# Campus Congestion
Building a smart mirror with RPi 4 that shows a human density map on campus. 
Please look in the "report" folder for an html file of the report.

## File Descriptions

### mult_webscraper.py
This file scrapes MRTG websites as provided by Cornell IT for network traffic information at the Access Point level.

### mirror_display.py
The heavy lifter of the project, this and the mult_webscraper.py are the two Python scripts that do a bulk of the work. The map of Duffield is in the folder /img, and similarly pictures of the network traffic graphs are stored in the folder /img. To run the project, run the following command in Terminal while in this folder: 
`sudo python3 mirror_display.py`

## Legacy files from project early stages

### MACAddr.sh
This shell script automatically finds the wlan0 (wifi) IP address and scan the devices connected to the network.
Also, it saves the data to the MAC_addr.txt file in a format of MAC address and device name.
Unknown device exists.

### test_output_1.txt
The output txt file when ```sudo nmap -sn $IP``` was ran.

### test_output_2.txt
The output txt file when ```sudo nmap -sn -oG $IP``` was ran.

## Hardware Requirements
Vanilla RPi 4 with piTFT and Raspberry Cobbler expansion cable.