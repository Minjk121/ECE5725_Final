from contextlib import redirect_stderr
from ossaudiodev import control_labels
import time
import RPi.GPIO as GPIO
import sys
import pygame
from pygame.locals import * # for event MOUSE variables
import os
import mult_webscraper
import datetime

## pygame/piTFT setup
os.putenv('SDL_VIDEODRIVER','fbcon') 
os.putenv('SDL_FBDEV','/dev/fb0') #so that this will be visible on the monitor

# in case the Pi freezes
t0 = time.time()
end_time = t0 + 600 # changed timeout to 10 min 
update_time = t0 + 300 # update traffic rates by 5 min

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
SKYBLUE=137,207,240

# Full monitor mode
infoObject = pygame.display.Info()
screen=pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
my_font = pygame.font.Font(None, 40) # 25
# these store the screen coordinates of the logs
menu_buttons={'congestion map':(1100,450),'study spaces':(1100,650)}
congestion_menu={'Phillips':(1140,373),'Duffield':(932,467),'Upson':(1012,629),'Rhodes':(1200,872),"main menu":(1500,1000)}
# the space list colors have been renamed so that we can actually sort them; 1 = green, 2 = yellow, 3 = red
space_list={'Duffield atrium':'1','ECE lounge':'1','Upson 2nd floor':'1','Upson 3rd floor':'1','CIS lounge':'1','Rhodes 3rd floor':'1','Rhodes 4th floor':'1','Rhodes 5th floor':'1'}
space_list_pos={1:(1000,100),2:(1000,300),3:(1000,500),4:(1000,700),5:(1000,900)}
# space_list_pos={'1':(1000,100),'2':(1000,300),'3':(1000,500),'4':(1000,700),'5':(1000,900), 'main menu': (1500, 1000)}

# congestion_data contains study spaces + halls
congestion_df = mult_webscraper.main() # data frame
congestion_data = mult_webscraper.convert_df_to_dict(congestion_df) # dictionary
''' 
{'Duffield atrium': 15053.199999999999, 'ECE lounge': 139.8, 'Upson 2nd floor': 6562.700000000001, 
'Upson 3rd floor': 9788.3, 'CIS lounge': 11801.9, 'Rhodes 3rd floor': 7744.799999999999, 
'Rhodes 4th floor': 7257.500000000001, 'Rhodes 5th floor': 1268.6, 'Phillips': 139.8, 'Duffield': 15053.199999999999,
 'Upson': 16351.0, 'Rhodes': 28072.8} 
 '''

# thresholds in kb, additive
level_red = 10000.0
level_yellow = 5000.0
level_green = 0.0

screen.fill(BLACK) # erase the workspace
menu_buttons_rect={} 
graph_buttons_rect={}
space_buttons_rect={}

menu_level = 1  # start on "main menu"
hall_name = ''

def determine_congestion_level():
    for study_space in space_list:
        current_traffic = congestion_data[study_space]
        if current_traffic > level_red:
            space_list[study_space] = '3' #red
        elif current_traffic > level_yellow:
            space_list[study_space] = '2' #yellow
        else:
            space_list[study_space] = '1' #green

# updates and returns dictionary type of congestion data
def update_congestion_data():
    df = mult_webscraper.main() # data frame
    return mult_webscraper.convert_df_to_dict(df)

# creates a margin between text and text box
def create_text_box(displayString, text_color, box_color, margin_x, margin_y):
    text_surface = my_font.render(displayString, True, text_color)
    box_surface = pygame.Surface(text_surface.get_rect().inflate(margin_x, margin_y).size)
    box_surface.fill(BLACK)
    box_surface.blit(text_surface, text_surface.get_rect(center = box_surface.get_rect().center))
    pygame.draw.rect(box_surface, box_color, box_surface.get_rect(center = box_surface.get_rect().center), 2)

    return box_surface

def updateSurfaceAndRect(buttons):
    for my_text, text_pos in buttons.items():
        displayString = my_text
        # text_surface = my_font.render(displayString, True, WHITE)
        text_surface = create_text_box(displayString, WHITE, SKYBLUE, 50,50)
        rect = text_surface.get_rect(center=text_pos)
        screen.blit(text_surface, rect)
        menu_buttons_rect[my_text] = rect

    if menu_level == 2:
        #print("congestion menu clicked")
        for study_space, text_pos in buttons.items():
            if (study_space != "main menu"):
                current_traffic = congestion_data[study_space]
                # TODO: congestion_data should be updated in every 5 minutes
                if current_traffic > level_red:
                    pygame.draw.circle(screen, RED, text_pos, 85, 4)
                elif current_traffic > level_yellow:
                    pygame.draw.circle(screen, YELLOW, text_pos, 85, 4)
                else:
                    pygame.draw.circle(screen, GREEN, text_pos, 85, 4) 

def updateSurfaceAndRect_StudySpace():
    #space_list_ordered = sorted(space_list,key=space_list.get)
    index = 1
    for space, v in sorted(space_list.items()):
        if (index < 6):
            displayString = "#"+str(index)+": "+space
            text_surface = create_text_box(displayString, WHITE, SKYBLUE, 50, 50)
            rect = text_surface.get_rect(center=space_list_pos[index])
            screen.blit(text_surface, rect)
            menu_buttons_rect[space] = rect
            index += 1
    text_surface = create_text_box('main menu', WHITE, SKYBLUE, 50, 50)
    rect = text_surface.get_rect(center=congestion_menu['main menu'])
    screen.blit(text_surface, rect)
    menu_buttons_rect['main menu'] = rect
             
        
def updateScreen():
    screen.fill(BLACK)
    if menu_level == 1: # main menu
        updateSurfaceAndRect(menu_buttons)
        
    elif menu_level ==2: # congestion map
        determine_congestion_level()
        # map is shown properly on monitor
        campus_map = pygame.image.load('./img/map.png')
        campus_map = pygame.transform.scale(campus_map, (1400, 1080)) # TODO: change to full screen & update coordinates of halls
        screen.blit(campus_map, (250,0))
        updateSurfaceAndRect(congestion_menu)
    elif menu_level == 3: # study spaces
        determine_congestion_level()
        updateSurfaceAndRect_StudySpace()

        
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
                        #pygame.draw.circle(screen, (139,0,0), (160,120),35,0)
                        newText = my_text
                        newRect = rect
                        updateScreen()
                        break
                    if (my_text=='study spaces'):
                        menu_level = 3
                        tempText = my_text
                        menu_buttons['main menu'] =  menu_buttons.pop('study spaces')
                        newText = my_text
                        newRect = rect
                        hall_name = my_text.lower()
                        updateScreen()
                        break
                    # congestion map clicked & shows dashboard (menu 2->3)
                    # TODO: check if this works
                    if (my_text in congestion_menu and menu_level == 2):
                        menu_level = 3
                        tempText = my_text
                        menu_buttons['congestion map'] = menu_buttons.pop('dashboard')
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
