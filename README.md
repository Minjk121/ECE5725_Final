# ECE5725_Final
Building a smart mirror with RPi 4 that shows a human density map on campus. This project is for ECE5725 and worked by Esther In and Minjung Kwon.. 

### Caution
nmap, ifconfig should be installed with ```sudo apt-get install``` first.
nmap does not work on WSL or Ubuntu LTS. This project is worked on RPi Linux OS.

## File descriptions

### MACAddr.sh
This shell script automatically finds the wlan0 (wifi) IP address and scan the devices connected to the network.
Also, it saves the data to the MAC_addr.txt file in a format of MAC address and device name.
Unknown device exists.

### test_output_1.txt
The output txt file when ```sudo nmap -sn $IP``` was ran.

### test_output_2.txt
The output txt file when ```sudo nmap -sn -oG $IP``` was ran.

## hardware 
Model repo: https://github.com/Junyi1995/MagicSelfieMirror
