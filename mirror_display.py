from contextlib import redirect_stderr
from ossaudiodev import control_labels
import time
import RPi.GPIO as GPIO
import sys
import pygame
from pygame.locals import * # for event MOUSE variables
import os
import mult_webscraper

## pygame/piTFT setup
os.putenv('SDL_VIDEODRIVER','fbcon') 
os.putenv('SDL_FBDEV','/dev/fb0') #so that this will be visible on the monitor

# in case the Pi freezes
t0 = time.time()
end_time = t0 + 60 # changed timeout to 60 sec

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# initialize pygame for piTFT 
pygame.init()
# pygame.mouse.set_visible(False)
WHITE=255,255,255
BLACK=0,0,0
RED=139,0,0
GREEN=0,128,0
YELLOW=255,255,0

# Full monitor mode
infoObject = pygame.display.Info()
screen=pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
my_font = pygame.font.Font(None, 40) # 25
# these store the screen coordinates of the logs
menu_buttons={'congestion map':(1100,450),'study spaces':(1100,650)}
congestion_menu={'phillips':(1140,373),'duffield':(932,467),'upson':(1012,629),'rhodes':(1200,872)}
space_list={'Duffield atrium':'green','ECE lounge':'green','Upson 2nd floor':'green','Upson 3rd floor':'green','CIS lounge':'green','Rhodes 3rd floor':'green','Rhodes 4th floor':'green','Rhodes 5th floor':'green'}

# updated in the helper function below
congestion_data = mult_webscraper.main()
# {'Duffield atrium': 24279.1, 'ECE lounge': 3084.5, 'Upson 2nd floor': 8187.6, 'Upson 3rd floor': 378.9, 'CIS lounge': 23667.4, 'Rhodes 3rd floor': 5300.0, 'Rhodes 4th floor': 14697.4, 'Rhodes 5th floor': 1512.7}

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

# updates and returns dictionary type of congestion data
def update_congestion_data():
    return mult_webscraper.main()

def updateSurfaceAndRect(buttons):
    for my_text, text_pos in buttons.items():
        displayString = my_text
        text_surface = my_font.render(displayString, True, WHITE)
        rect = text_surface.get_rect(center=text_pos)
        screen.blit(text_surface,rect)
        menu_buttons_rect[my_text] = rect
    #if it's the congestion menu
    # TODO: this might not work, need to double check
    if buttons=='congestion_menu':
        for study_space, text_pos in buttons.items():
            current_traffic = congestion_data[study_space]
            # TODO: congestion_data should be updated in every 5 minutes
            if current_traffic > level_red:
                pygame.draw.circle(screen, RED, text_pos, 15, 0)
            elif current_traffic > level_yellow:
                pygame.draw.circle(screen, YELLOW, text_pos, 15, 0)
            else:
                pygame.draw.circle(screen, GREEN, text_pos, 15, 0)
    
    #TODO: if it's the study spaces menu
    # if buttons=='study spaces':
    #     for study_space in space_list:
    #         # TODO: draw rects for each loc
    #         pygame.draw.rect(screen, YELLOW, text_pos, 15, 0)
        
def updateScreen():
    screen.fill(BLACK)
    if menu_level == 1:
        updateSurfaceAndRect(menu_buttons)
        pygame.draw.rect(screen, RED, list(menu_buttons_rect.values())[0])
        pygame.draw.rect(screen, GREEN, list(menu_buttons_rect.values())[1])
    elif menu_level ==2:
        determine_congestion_level()
        # TODO: check if the map image is shown on monitor
        campus_map = pygame.image.load('./img/map.png')
        campus_map = pygame.transform.scale(campus_map, (1400, 1080))
        campus_map_rect = campus_map.get_rect()       
        screen.blit(campus_map, (250,0))
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
