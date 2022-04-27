#!/bin/bash

# this code creates and saves the MAC addr and device name into MAC_addr.txt file

# sudo nmap -sn 10.49.30.241/24 | grep MAC | awk '{print $3","$4","$5}' > MAC_addr.txt

IP=$(hostname -I)  # gets IP addr of wifi (wlan0)
#echo ${IP// /}/24

sudo nmap -sn ${IP// /}/24 | grep MAC | awk '{print $3","$4","$5}' > MAC_addr.txt
cat MAC_addr.txt
