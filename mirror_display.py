from contextlib import redirect_stderr
from ossaudiodev import control_labels
import time
import RPi.GPIO as GPIO
import sys
import pygame
from pygame.locals import * # for event MOUSE variables
import os

## pygame/piTFT setup
os.putenv('SDL_VIDEODRIVER','fbcon') 
os.putenv('SDL_FBDEV','/dev/fb0') #so that this will be visible on the monitor

# in case the Pi freezes
t0 = time.time()
end_time = t0 + 30

GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)

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
# TODO: find the coordinates on the map and add them below
congestion_menu={'duffield':(0,0),'upson':(0,0),'another study space':(0,0)}
space_list={'Duffield atrium':'green','ECE lounge':'green','Upson 2nd floor':'green','Upson 3rd floor':'green','CIS lounge':'green','Rhodes 3rd floor':'green','Rhodes 4th floor':'green','Rhodes 5th floor':'green'}

# TODO: need to somehow import the congestion level data from the webscraper and put in below as dictionary
congestion_data={''}
# thresholds in kb, additive
level_red = 10000
level_yellow = 5000
level_green = 0

screen.fill(BLACK) # erase the workspace
menu_buttons_rect={}
menu_level = 1  # start on "main menu"

def determine_congestion_level():
    for study_space in space_list.items():
        current_traffic = congestion_data[study_space]
        if current_traffic > level_red:
            space_list[study_space] = 'red'
        elif current_traffic > level_yellow:
            space_list[study_space] = 'yellow'
        else:
            space_list[study_space] = 'green'

def updateSurfaceAndRect(buttons):
    for my_text, text_pos in buttons.items():
        displayString = my_text
        text_surface = my_font.render(displayString, True, WHITE)
        rect = text_surface.get_rect(center=text_pos)
        screen.blit(text_surface,rect)
    #if it's the congestion menu
    # TODO: this might not work, need to double check
    if buttons=='congestion_menu':
        for study_space, text_pos in buttons.items():
            current_traffic = congestion_data[study_space]
            if current_traffic > level_red:
                pygame.draw.circle(screen, RED, text_pos, 15, 0)
            elif current_traffic > level_yellow:
                pygame.draw.circle(screen, YELLOW, text_pos, 15, 0)
            else:
                pygame.draw.circle(screen, GREEN, text_pos, 15, 0)
        
def updateScreen():
    screen.fill(BLACK)
    if menu_level == 1:
        updateSurfaceAndRect(menu_buttons)
        pygame.draw.rect(screen, RED, menu_buttons_rect[0])
        pygame.draw.rect(screen, GREEN, menu_buttons_rect[1])
    elif menu_level ==2:
        determine_congestion_level()
        # TODO: need to draw the map (import image?)
        campus_map = pygame.image.load("campus_map.png")
        campus_map_rect = campus_map.get_rect()
        updateSurfaceAndRect(congestion_menu)
        
    pygame.display.flip()


updateScreen()

while (time.time() < end_time):
    time.sleep(0.2)
    #stop_button()
    for event in pygame.event.get():
        if (event.type is MOUSEBUTTONDOWN):
            pos = pygame.mouse.get_pos()
        elif (event.type is MOUSEBUTTONUP):
            pos = pygame.mouse.get_pos()
            x,y = pos
            for (my_text, rect) in menu_buttons_rect.items():
                if (rect.collidepoint(pos)):
                    if (my_text=='congestion map'):
                        # print('hit congestion map')
                        menu_level = 2
                        tempText = my_text
                        menu_buttons['main menu'] = menu_buttons.pop('congestion map')
                        newText = my_text
                        newRect = rect
                        updateScreen()
                        break
                    if (my_text=='main menu'):
                        menu_level = 1
                        tempText = my_text
                        menu_buttons['congestion map'] = menu_buttons.pop('main menu')
                        newText = my_text
                        newRect = rect
                        updateScreen()
                        break
                    if (my_text=='quit'):
                        sys.exit()
            del menu_buttons_rect[tempText]
            menu_buttons_rect[newText] = newRect
    if ( not GPIO.input(17) ):
        sys.exit()
    updateScreen()