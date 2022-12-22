# ==========================================================================
# mirror_display.py
# ==========================================================================
# uses data from mult_webscraper.py and displays the map, 
# charts and graphs to the monitor controlled by piTFT.

from contextlib import redirect_stderr
from ossaudiodev import control_labels
import time
import RPi.GPIO as GPIO
import sys
import pygame
from pygame.locals import * # for event MOUSE variables
import os
import mult_webscraper
from datetime import datetime
import requests
import pygame.display

# Pygame/PiTFT setup
os.putenv('SDL_VIDEODRIVER','fbcon') 
os.putenv('SDL_FBDEV','/dev/fb0') # makes visible on the monitor

# Timeout setup in case the Pi freezes
t0 = time.time()
end_time = t0 + 1200 # timeout after 10 min 
update_time = t0 + 300 # update traffic rates by 5 min

GPIO.setmode(GPIO.BCM)

# GPIO Button setup
# Exit/Panic button (closest to the motor driver)
GPIO.setup(13, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# Menu buttons (on the piTFT)
GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# "Main Menu" button (on the breadboard, closest to the cobbler)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Initializes pygame for piTFT 
pygame.display.init()
pygame.init()
WHITE=255,255,255
BLACK=0,0,0
RED=139,0,0
GREEN=0,128,0
YELLOW=255,255,0
SKYBLUE=137,207,240

# Variables for full display
infoObject = pygame.display.Info()
screen=pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
screen_width = infoObject.current_w
screen_height = infoObject.current_h
my_font = pygame.font.Font(None, 40) 

# Stores the screen coordinates of the logs
menu_buttons={'congestion map':(0.573*screen_width,0.417*screen_height),'study spaces':(0.573*screen_width,0.602*screen_height)}
congestion_menu={'Phillips':(0.593*screen_width,0.345*screen_height),'Duffield':(0.485*screen_width,0.432*screen_height),'Upson':(0.527*screen_width,0.582*screen_height),'Rhodes':(0.625*screen_width,0.807*screen_height),"main menu":(0.781*screen_width,0.926*screen_height)}

# Space list dictionaries (1 = green, 2 = yellow, 3 = red)
space_list={'Duffield atrium':'1','ECE lounge':'1','Upson 2nd floor':'1','Upson 3rd floor':'1','CIS lounge':'1','Rhodes 3rd floor':'1','Rhodes 4th floor':'1','Rhodes 5th floor':'1'}
space_list_pos={1:(0.521*screen_width,0.093*screen_height),2:(0.521*screen_width,0.278*screen_height),3:(0.521*screen_width,0.463*screen_height),4:(0.521*screen_width,0.648*screen_height),5:(0.521*screen_width,0.833*screen_height),"main menu":(0.781*screen_width,0.926*screen_height)}

# Adds remote control/button functionality
recommended_spaces_list = [] 

# Calls congestion_data containing study space & hall data
df = mult_webscraper.main()
congestion_df = df[0]
congestion_df_dashboard = df[1]

# Converts to dictionary type
congestion_data = mult_webscraper.convert_df_to_dict(congestion_df)

# Sets thresholds in Mb/s, additive
level_red = 200.0
level_yellow = 100.0
level_green = 0.0

# Erases the workspace
screen.fill(BLACK) 
menu_buttons_rect={} 
graph_buttons_rect={}
congestion_buttons_rect={}
space_buttons_rect={}

# Starts on "main menu"
menu_level = 1  
hall_name = ''
dashboard_hall = ''

# ==========================================================================
# determine_congestion_level.py
# ==========================================================================
# Determines congestion level based on the congestion_data dictionary
# from the webscraper and converted from the dataframe

def determine_congestion_level():
    for study_space in space_list:
        current_traffic = congestion_data[study_space]
        if current_traffic > level_red:
            space_list[study_space] = '3' #red
        elif current_traffic > level_yellow:
            space_list[study_space] = '2' #yellow
        else:
            space_list[study_space] = '1' #green

# ==========================================================================
# update_congestion_data()
# ==========================================================================
# Updates and returns dictionary type of congestion data
def update_congestion_data():
    df = mult_webscraper.main() # data frame
    return mult_webscraper.convert_df_to_dict(df[0])

# ==========================================================================
# create_text_box()
# ==========================================================================
# Creates a margin between text and text box

def create_text_box(displayString, text_color, box_color, margin_x, margin_y):
    if text_color == SKYBLUE: 
        my_font = pygame.font.Font(None, 25) 
    else: 
        my_font = pygame.font.Font(None, 40) # 25
    text_surface = my_font.render(displayString, True, text_color)
    box_surface = pygame.Surface(text_surface.get_rect().inflate(margin_x, margin_y).size)
    box_surface.fill(BLACK)
    box_surface.blit(text_surface, text_surface.get_rect(center = box_surface.get_rect().center))
    pygame.draw.rect(box_surface, box_color, box_surface.get_rect(center = box_surface.get_rect().center), 2)

    return box_surface

# ==========================================================================
# updateSurfaceAndRect()
# ==========================================================================
# Generalized helper function to update the surfaces and rects
# Input: buttons, the dictionary; no outputs

def updateSurfaceAndRect(buttons):
    for my_text, text_pos in buttons.items():
        displayString = my_text
        # text_surface = my_font.render(displayString, True, WHITE)
        text_surface = create_text_box(displayString, WHITE, SKYBLUE, 50,50)
        rect = text_surface.get_rect(center=tuple(map(int,text_pos)))
        screen.blit(text_surface, rect)
        if (menu_level == 1):
            menu_buttons_rect[my_text] = rect
        elif (menu_level == 2):
            congestion_buttons_rect[my_text] = rect

    if menu_level == 1:
        # Adds time to the screen
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        my_font = pygame.font.Font(None, 100) 
        text_surface = my_font.render(current_time, True, WHITE)
        rect = text_surface.get_rect(center=tuple(map(int,(0.373*screen_width,0.417*screen_height))))
        screen.blit(text_surface, rect)
    
    if menu_level == 2:
        for study_space, text_pos in buttons.items():
            if (study_space != "main menu"):
                current_traffic = congestion_data[study_space]
                if current_traffic > level_red:
                    pygame.draw.circle(screen, RED, tuple(map(int,text_pos)), 85, 4)
                elif current_traffic > level_yellow:
                    pygame.draw.circle(screen, YELLOW, tuple(map(int,text_pos)), 85, 4)
                else:
                    pygame.draw.circle(screen, GREEN, tuple(map(int,text_pos)), 85, 4) 

# ==========================================================================
# updateSurfaceAndRect_StudySpace()
# ==========================================================================
# Specialized helper function to update the surfaces and rects of the study space list
# Considers the top five least congested areas for study space recommendations
# Default ordering is in alphabetical order (popular spaces like CIS lounge, ECE lounge, and Duffield)
# If all else are equal, always show up near the top 
# Function takes no inputs, return nothing, in-line edit recommend_spaces_list for top 4 study spaces

def updateSurfaceAndRect_StudySpace():
    index = 1
    congestion_colors = ['green','yellow','red']
    for space in sorted(space_list,key=space_list.get):
        if (index < 5):
            v = space_list[space]
            congestion_level = congestion_colors[int(v)-1]
            displayString = "#"+str(index)+": "+space+" (level "+congestion_level+")"
            text_surface = create_text_box(displayString, WHITE, SKYBLUE, 50, 50)
            rect = text_surface.get_rect(center=space_list_pos[index])
            screen.blit(text_surface, rect)
            space_buttons_rect[space] = rect
            index += 1
            recommended_spaces_list.append(space)
    
    # Draws main menu button
    text_surface = create_text_box('main menu', WHITE, SKYBLUE, 50, 50)
    rect = text_surface.get_rect(center=space_list_pos['main menu'])
    screen.blit(text_surface, rect)
    menu_buttons_rect['main menu'] = rect


#==================================================================================================
# determine_route()
#==================================================================================================
# Determines the route from outside of the engineering quad buildings to a specified study "space"
# Takes one input & Returns an ordered array of the recommended route (starting from index 0)

def determine_route(space):
 
    # Duffield atrium and ECE lounge accesible without crossing through any other area; short circuit
    if (space == 'Duffield atrium'): return ['Duffield']
    if (space == 'ECE lounge'): return ['Phillips']

    # Short circuit: if duffield, phillips, and upson are all congested, skip them and go straight to upson/rhodes
    if ('Rhodes' in space) and (space_list['Duffield atrium'] == 3 and space_list['ECE lounge'] == 3):
        return ["Rhodes"]

    # Otherwise, determine route through buildings
    # the values, even in strings, can be compared with operators such as >, <, >=, etc
    route = []

    # Start from duffield atrium if it is green or yellow level, otherwise start at phillips
    # But if phillips is red then go through upson instead
    route_start = ""
    if (int(space_list['Duffield atrium']) <= 2):
        route_start = "Duffield"
    elif (int(space_list['ECE lounge']) <=2):
        route_start = "Phillips"
    else: route_start = "Upson"
    route.append(route_start)

    # If in rhodes, need to go through upson; if in upson, of course go through upson
    route.append('Upson')
    
    # If in upson, end here
    if ('Upson' in space):
        #print (route)
        return route
    
    # If nothing above and code comes all the way down here, the space must be in rhodes
    route.append('Rhodes')
    #print("THE ROUTE IS ",route)
    return route

#==================================================================================================
# draw_route_on_map()
#==================================================================================================
# Shows map and draws a route on it

def draw_route_on_map(route):
 
    # Draws the line between each label
    # Order of drawing matters - the line appears behind the label
    for i in range(len(route) - 1):
        line_start_pos = tuple(map(int,congestion_menu[route[i]]))
        line_end_pos = tuple(map(int,congestion_menu[route[i+1]]))
        pygame.draw.line(screen, BLACK, line_start_pos, line_end_pos, 5) # increases the last parameter for thicker line

    # Draws label on the map for each item in the route 
    for i in range(len(route)):
        my_text = route[i]
        displayString = my_text
        box_color = SKYBLUE if (i != (len(route)-1)) else RED
        text_surface = create_text_box(displayString, WHITE, box_color, 50, 50)
        text_pos = congestion_menu[my_text]
        rect = text_surface.get_rect(center=tuple(map(int,text_pos)))
        screen.blit(text_surface, rect)
    
    # Draws main menu button
    text_surface = create_text_box('main menu', WHITE, SKYBLUE, 50, 50)
    rect = text_surface.get_rect(center=tuple(map(int,congestion_menu['main menu'])))
    screen.blit(text_surface, rect)
    congestion_buttons_rect['main menu'] = rect

#==================================================================================================
# updateScreen()
#==================================================================================================
# General all-purpose use helper function to update screen
# OPTIONAL input argument: route, so that we can continue to use updateScreen as a generalized function
# while also correctly updating the route 

def updateScreen(route=[]):
    screen.fill(BLACK)

    # Main menu
    if menu_level == 1: 
        updateSurfaceAndRect(menu_buttons)
        
    # Congestion map
    elif menu_level ==2:
        determine_congestion_level()
        campus_map = pygame.image.load('./img/map.png')
        campus_map = pygame.transform.scale(campus_map, (screen_width, screen_height))
        screen.blit(campus_map, (0,0))
        updateSurfaceAndRect(congestion_menu)
    
    # Study space list
    elif menu_level == 3: 
        determine_congestion_level()
        recommended_spaces_list = updateSurfaceAndRect_StudySpace()
    
    # Network traffic dashboard
    elif menu_level == 4:
        mrtg_lst = mult_webscraper.convert_df_to_graph_lst(congestion_df, dashboard_hall)
        name_lst = mult_webscraper.convert_df_to_name_lst(congestion_df, dashboard_hall)
        change_orientation = False
        count = 1
        count_2 = 1
        text_surface = create_text_box(dashboard_hall.upper(), YELLOW, YELLOW, 10, 10)

        screen.blit(text_surface, (int(screen_width/2)-30,int(screen_height/8-50)))
        df = congestion_df_dashboard
        for images in mrtg_lst:
            # Draws mrtg graphs
            mrtg_graph = pygame.image.load("./img/"+images)
            text_surface = create_text_box(images.replace("png",''), SKYBLUE, SKYBLUE, 10, 10)

            if count >= 6:
                screen.blit(mrtg_graph, (int(screen_width/8)*4+30, int(screen_height/6) * count_2))
                screen.blit(text_surface, (int(screen_width/8)*4+30, int(screen_height/6) * count_2-30))
                count_2+=1
                change_orientation = True
            else:
                screen.blit(mrtg_graph, (int(screen_width/8), int(screen_height/6) * count))
                screen.blit(text_surface, (int(screen_width/8), int(screen_height/6) * count-30))
            count+=1

        count = 1

        if not change_orientation:
            for names in name_lst:
                text_info = create_text_box("Study Space           Current Traffic (Mb/s)", SKYBLUE, SKYBLUE, 10, 10)
                name_info = create_text_box(names, SKYBLUE, SKYBLUE, 10, 10)
                traff_info = create_text_box(str(congestion_data[names]), SKYBLUE, SKYBLUE, 10, 10)
                screen.blit(name_info, (int(screen_width/2)+50, int(screen_height/6) * count+30))
                screen.blit(traff_info, (int(screen_width/2)+250, int(screen_height/6) * count+30))
                screen.blit(text_info, (int(screen_width/2)+50, int(screen_height/6) * count))
                count+=1

        if change_orientation:
            count_2 = 1
            for names in name_lst:
                name_info = create_text_box(names+":  ", SKYBLUE, SKYBLUE, 10, 10)
                traff_info = create_text_box(str(congestion_data[names])+"Mb/s", SKYBLUE, SKYBLUE, 10, 10)
                if count >=6:
                    screen.blit(name_info, (int(screen_width/8)*4+270, int(screen_height/6) * count_2-30))
                    screen.blit(traff_info, (int(screen_width/8)*4+400, int(screen_height/6) * count_2-30))
                    count_2+=1
                else:
                    screen.blit(name_info, (int(screen_width/4)+50, int(screen_height/6) * count-30))
                    screen.blit(traff_info, (int(screen_width/8)+370, int(screen_height/6) * count-30))
                count+=1

    # Recommended route on map
    elif menu_level == 5:
        # Loads a campus map image file
        campus_map = pygame.image.load('./img/map.png')
        campus_map = pygame.transform.scale(campus_map, (screen_width, screen_height))
        screen.blit(campus_map, (0,0))

        draw_route_on_map(route)
        
    pygame.display.flip()

### Initializes screen
updateScreen()

### While within the run time limit
while (time.time() < end_time):
    time.sleep(0.2)

    # Updates the congestion level data in script every five minutes
    if time.time() > update_time:
        congestion_data = update_congestion_data()
        determine_congestion_level()
        if menu_level == 2:
            # Also detects menu_level to update the surface & rect properly
            updateScreen() 
        update_time = time.time() + 300

    for event in pygame.event.get():
        if (event.type is MOUSEBUTTONDOWN):
            pos = pygame.mouse.get_pos()
        elif (event.type is MOUSEBUTTONUP):
            pos = pygame.mouse.get_pos()
            x,y = pos
            buttons_rect_list = {}
            if (menu_level == 1):
                buttons_rect_list = menu_buttons_rect
            elif (menu_level == 2):
                buttons_rect_list = congestion_buttons_rect
            elif (menu_level == 3):
                buttons_rect_list = space_buttons_rect
            else:
                buttons_rect_list = menu_buttons_rect
            for (my_text, rect) in buttons_rect_list.items():
                if (rect.collidepoint(pos)):
                    if (my_text=='congestion map'):
                        menu_level = 2
                        updateScreen()
                        break
                    if (my_text=='main menu'): 
                        menu_level = 1
                        updateScreen()
                        break
                    if (my_text=='study spaces'):
                        menu_level = 3
                        hall_name = my_text.lower()
                        updateScreen()
                        break
                    # Congestion map clicked & shows dashboard
                    if (my_text in congestion_menu):
                        menu_level = 4
                        dashboard_hall = my_text
                        updateScreen()
                        break
                    if (my_text in space_list):
                        menu_level = 5
                        route = determine_route(my_text)
                        menu_level = 5 #go to routing
                        updateScreen(route)
                        break
                    if (my_text=='quit'):
                        sys.exit()
    
    # For button presses, when doing "remote control" of the menu
    # If in congestion map, the buttons are top-to-bottom sequential
    if (menu_level == 1):
        if ( not GPIO.input(27) ):
            menu_level = 2 # go to congestion map
            updateScreen()
        if ( not GPIO.input(23) ):
            menu_level = 3 # go to study spaces
            updateScreen()

    elif (menu_level == 2):
        if ( not GPIO.input(27) ): # Phillips
            menu_level = 4 # go to dashboard
            dashboard_hall = 'Phillips'
            updateScreen()
        if ( not GPIO.input(23) ): # Duffield
            menu_level = 4 # go to dashboard
            dashboard_hall = 'Duffield'
            updateScreen()
        if ( not GPIO.input(22)): # Upson
            menu_level = 4 # go to dashboard
            dashboard_hall = 'Upson'
            updateScreen()
        if ( not GPIO.input(17)): #Rhodes
            menu_level = 4 # go to dashboard
            dashboard_hall = 'Rhodes'
            updateScreen()
    elif (menu_level == 3):
        if ( not GPIO.input(27) ):
            route = determine_route(recommended_spaces_list[0])
            menu_level = 5 # go to routing
            updateScreen(route)
        if ( not GPIO.input(23)):
            route = determine_route(recommended_spaces_list[1])
            menu_level = 5 # go to routing
            updateScreen(route)
        if ( not GPIO.input(22)):
            route = determine_route(recommended_spaces_list[2])
            menu_level = 5 # go to routing
            updateScreen(route)
        if ( not GPIO.input(17)):
            route = determine_route(recommended_spaces_list[3])
            menu_level = 5 # go to routing
            updateScreen(route)
    
    # Main menu button clicked
    if ( not GPIO.input(26) ):
        menu_level = 1
        updateScreen()
    # Panic button clicked
    if ( not GPIO.input(13) ):
        pygame.quit()
        sys.exit()

    if (menu_level==1):
        # Updates screen for time
        updateScreen()
