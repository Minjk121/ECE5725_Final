# import mult_webscraper
import RPi.GPIO as GPIO
import time
import sys

import pygame
from pygame.locals import * # for event MOUSE variables
import os

# d = mult_webscraper.main()
# print(d)
# print(type(d))

infoObject = pygame.display.Info()
print(infoObject.current_w, infoObject.current_h)
# pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
