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
congestion_menu={'Phillips':(1140,373),'Duffield':(932,467),'Upson':(1012,629),'Rhodes':(1200,872)}
space_list={'Duffield atrium':'green','ECE lounge':'green','Upson 2nd floor':'green','Upson 3rd floor':'green','CIS lounge':'green','Rhodes 3rd floor':'green','Rhodes 4th floor':'green','Rhodes 5th floor':'green'}
space_buttons={'Duffield atrium':(300, 300),'ECE lounge':(300, 400),'Upson 2nd floor':(300, 500),'Upson 3rd floor':(300, 600),'CIS lounge':(1100, 300),'Rhodes 3rd floor':(1100, 400),'Rhodes 4th floor':(1100, 500),'Rhodes 5th floor':(1100, 600)}


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
space_buttons_rect={}

menu_level = 1  # start on "main menu"

def determine_congestion_level():
    for study_space in space_list:
        current_traffic = congestion_data[study_space]
        if current_traffic > level_red:
            space_list[study_space] = 'red'
        elif current_traffic > level_yellow:
            space_list[study_space] = 'yellow'
        else:
            space_list[study_space] = 'green'

# updates and returns dictionary type of congestion data
def update_congestion_data():
    df = mult_webscraper.main() # data frame
    return mult_webscraper.convert_df_to_dict(df)

def create_text_box(displayString, text_color, box_color, margin_x, margin_y):
    text_surface = my_font.render(displayString, True, text_color)
    box_surface = pygame.Surface(text_surface.get_rect().inflate(margin_x, margin_y).size)
    box_surface.fill(box_color)
    box_surface.blit(text_surface, text_surface.get_rect(center = box_surface.get_rect().center))
    return box_surface

def updateSurfaceAndRect(buttons):
    for my_text, text_pos in buttons.items():
        displayString = my_text
        # text_surface = my_font.render(displayString, True, WHITE)
        text_surface = create_text_box(displayString, WHITE, BLACK, 50,50)
        rect = text_surface.get_rect(center=text_pos)
        screen.blit(text_surface, rect)
        menu_buttons_rect[my_text] = rect

    #if it's the congestion menu
    if menu_level == 2: #buttons=='congestion_menu':
        print("congestion menu clicked")
        for study_space, text_pos in buttons.items():
            current_traffic = congestion_data[study_space]
            # TODO: congestion_data should be updated in every 5 minutes
            if current_traffic > level_red:
                pygame.draw.circle(screen, RED, text_pos, 50, 0)
            elif current_traffic > level_yellow:
                pygame.draw.circle(screen, YELLOW, text_pos, 50, 0)
            else:
                pygame.draw.circle(screen, GREEN, text_pos, 50, 0) # maybe add ', 2' to draw circle without filling inside
            
def updateScreen():
    screen.fill(BLACK)
    if menu_level == 1:
        updateSurfaceAndRect(menu_buttons)
        # TODO: Add current time at a certain location & Add other images to menu (to look nicer?) 
        # curr_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        pygame.draw.rect(screen, RED, list(menu_buttons_rect.values())[0], 2)
        pygame.draw.rect(screen, GREEN, list(menu_buttons_rect.values())[1], 2)
    elif menu_level == 2:
        determine_congestion_level()
        campus_map = pygame.image.load('./img/map.png')
        campus_map = pygame.transform.scale(campus_map, (1400, 1080))
        campus_map_rect = campus_map.get_rect()       
        screen.blit(campus_map, (250,0))
        updateSurfaceAndRect(congestion_menu)
    
    elif menu_level == 3: # when map is clicked, shows traffic data & diagram of study spaces
        # load image of study space (multiple if upson / rhodes)
        # load mrtg graph
        mrtg_graph = pygame.image.load()
        # load congestion data (Daily - max & avg & curr)
    
    elif menu_level == 4: # space_list 
        # list of study spaces
        updateSurfaceAndRect(space_buttons)
        for position in space_buttons_rect.values()
            pygame.draw.rect(screen, SKYBLUE, position, 2)
        
    elif menu_level == 5:  # when destination space is clicked, recommend a route
        # state machine
        print("Enter through Duffield")
        
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
