import mult_webscraper
from varname import nameof
import requests

# import RPi.GPIO as GPIO
# import time
# import sys

# import pygame
# from pygame.locals import * # for event MOUSE variables
# import os

# d = mult_webscraper.main()
# print(d)
# print(type(d))
# print(type(d['ECE lounge']))
congestion_menu = {'Test':'tmp', '2':'two'}
name = "Test"
if name in congestion_menu:
    print("!")

response = requests.get("http://mrtg.cit.cornell.edu/switch/WorkDir/duffield2-5400.120-day.png")

file = open("tmp.png", "wb")
file.write(response.content)
file.close()
# pygame.init()
# infoObject = pygame.display.Info()
# print(infoObject.current_w, infoObject.current_h)
# pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
