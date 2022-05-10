import time
import RPi.GPIO as GPIO
import sys
import pygame
from pygame.locals import * # for event MOUSE variables
import os

## pygame/piTFT setup
os.putenv('SDL_VIDEODRIVER','fbcon') 
os.putenv('SDL_FBDEV','/dev/fb0') #so that this will be visible on the monitor

# initialize pygame for piTFT 
pygame.init()
pygame.mouse.set_visible(False)
WHITE=255,255,255
BLACK=0,0,0
RED=139,0,0
GREEN=0,128,0
YELLOW=255,255,0
screen=pygame.display.set_mode((320,240))
my_font = pygame.font.Font(None, 25)
# these store the screen coordinates of the logs
menu_buttons={'congestion map':(160,120),'study spaces':(270,200)}

def updateSurfaceAndRect(buttons):
    for my_text, text_pos in buttons.items():
        displayString = my_text
        text_surface = my_font.render(displayString, True, WHITE)
        rect = text_surface.get_rect(center=text_pos)
        screen.blit(text_surface,rect)

def updateScreen():
    screen.fill(BLACK)
    updateSurfaceAndRect(menu_buttons)
    pygame.draw.rect(screen, RED, menu_buttons_rect[0])
    pygame.draw.rect(screen, GREEN, menu_buttons_rect[1])    
    pygame.display.flip()


updateScreen()
t0 = time.time()
end_time = t0 + 30
while (time.time() < end_time):
    time.sleep(0.2)
    updateScreen()
