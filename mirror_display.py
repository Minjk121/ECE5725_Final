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
import requests
import pygame.display

## pygame/piTFT setup
os.putenv('SDL_VIDEODRIVER','fbcon') 
os.putenv('SDL_FBDEV','/dev/fb0') #so that this will be visible on the monitor

# in case the Pi freezes
t0 = time.time()
end_time = t0 + 600 # changed timeout to 10 min 
update_time = t0 + 300 # update traffic rates by 5 min

GPIO.setmode(GPIO.BCM)
# exit/panic button; the button closest to the motor driver
GPIO.setup(13, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# menu buttons (on the piTFT)
GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# "main menu" button (on the breadboard, closest to the cobbler)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# initialize pygame for piTFT 
pygame.display.init()
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
screen_width = infoObject.current_w
screen_height = infoObject.current_h
my_font = pygame.font.Font(None, 40) # 25
# these store the screen coordinates of the logs
menu_buttons={'congestion map':(0.573*screen_width,0.417*screen_height),'study spaces':(0.573*screen_width,0.602*screen_height)}
congestion_menu={'Phillips':(0.593*screen_width,0.345*screen_height),'Duffield':(0.485*screen_width,0.432*screen_height),'Upson':(0.527*screen_width,0.582*screen_height),'Rhodes':(0.625*screen_width,0.807*screen_height),"main menu":(0.781*screen_width,0.926*screen_height)}
# menu_buttons={'congestion map':(1100,450),'study spaces':(1100,650)}
# congestion_menu={'Phillips':(1140,373),'Duffield':(932,467),'Upson':(1012,629),'Rhodes':(1200,872),"main menu":(1500,1000)}

# the space list colors have been renamed so that we can actually sort them; 1 = green, 2 = yellow, 3 = red
space_list={'Duffield atrium':'1','ECE lounge':'1','Upson 2nd floor':'1','Upson 3rd floor':'1','CIS lounge':'1','Rhodes 3rd floor':'1','Rhodes 4th floor':'1','Rhodes 5th floor':'1'}
space_list_pos={1:(0.521*screen_width,0.093*screen_height),2:(0.521*screen_width,0.278*screen_height),3:(0.521*screen_width,0.463*screen_height),4:(0.521*screen_width,0.648*screen_height),5:(0.521*screen_width,0.833*screen_height),"main menu":(0.781*screen_width,0.926*screen_height)}
# space_list_pos={1:(1000,100),2:(1000,300),3:(1000,500),4:(1000,700),5:(1000,900)}
# space_list_pos={'1':(1000,100),'2':(1000,300),'3':(1000,500),'4':(1000,700),'5':(1000,900), 'main menu': (1500, 1000)}

# need this for remote control/button functionality
recommended_spaces_list = [] 

# congestion_data contains study spaces + halls
df = mult_webscraper.main()
congestion_df = df[0] # data frame
congestion_df_dashboard = df[1] # df for dashboard
congestion_data = mult_webscraper.convert_df_to_dict(congestion_df) # dictionary
''' 
{'Duffield atrium': 15053.199999999999, 'ECE lounge': 139.8, 'Upson 2nd floor': 6562.700000000001, 
'Upson 3rd floor': 9788.3, 'CIS lounge': 11801.9, 'Rhodes 3rd floor': 7744.799999999999, 
'Rhodes 4th floor': 7257.500000000001, 'Rhodes 5th floor': 1268.6, 'Phillips': 139.8, 'Duffield': 15053.199999999999,
 'Upson': 16351.0, 'Rhodes': 28072.8} 
 '''

# thresholds in Mb, additive
level_red = 200.0 #Mb/s
level_yellow = 100.0 #Mb/s
level_green = 0.0

screen.fill(BLACK) # erase the workspace
menu_buttons_rect={} 
graph_buttons_rect={}
congestion_buttons_rect={}
space_buttons_rect={}

menu_level = 1  # start on "main menu"
hall_name = ''
dashboard_hall = ''

# helper function to determine congestion level based on the congestion_data dictionary
# (which is from the webscraper and converted from the dataframe)
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
    return mult_webscraper.convert_df_to_dict(df[0])

# creates a margin between text and text box
def create_text_box(displayString, text_color, box_color, margin_x, margin_y):
    if text_color == SKYBLUE: 
        my_font = pygame.font.Font(None, 25) 
    else: my_font = pygame.font.Font(None, 40) # 25
    text_surface = my_font.render(displayString, True, text_color)
    box_surface = pygame.Surface(text_surface.get_rect().inflate(margin_x, margin_y).size)
    box_surface.fill(BLACK)
    box_surface.blit(text_surface, text_surface.get_rect(center = box_surface.get_rect().center))
    pygame.draw.rect(box_surface, box_color, box_surface.get_rect(center = box_surface.get_rect().center), 2)

    return box_surface

# generalized helper function to update the surfaces and rects
# input: buttons, the dictionary
# no outputs
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

    if menu_level == 2:
        #print("congestion menu clicked")
        for study_space, text_pos in buttons.items():
            if (study_space != "main menu"):
                current_traffic = congestion_data[study_space]
                if current_traffic > level_red:
                    pygame.draw.circle(screen, RED, tuple(map(int,text_pos)), 85, 4)
                elif current_traffic > level_yellow:
                    pygame.draw.circle(screen, YELLOW, tuple(map(int,text_pos)), 85, 4)
                else:
                    pygame.draw.circle(screen, GREEN, tuple(map(int,text_pos)), 85, 4) 

# specialized helper function to update the surfaces and rects of the study space list
# we will only consider the top five least congested areas for study space recommendations
# default ordering is in alphabetical order, such that popular spaces like CIS lounge, ECE lounge, and Duffield
# always show up near the top (if all else are equal)
# function takes no inputs, return nothing, in-line edit recommend_spaces_list for top 4 study spaces
def updateSurfaceAndRect_StudySpace():
    #space_list_ordered = sorted(space_list,key=space_list.get)
    index = 1
    for space, v in sorted(space_list.items()):
        if (index < 5):
            congestion_colors = ['green','yellow','red']
            congestion_level = congestion_colors[int(v)-1]
            displayString = "#"+str(index)+": "+space+" (level "+congestion_level+")"
            text_surface = create_text_box(displayString, WHITE, SKYBLUE, 50, 50)
            rect = text_surface.get_rect(center=space_list_pos[index])
            screen.blit(text_surface, rect)
            space_buttons_rect[space] = rect
            index += 1
            recommended_spaces_list.append(space)
    
    # draw main menu button
    text_surface = create_text_box('main menu', WHITE, SKYBLUE, 50, 50)
    rect = text_surface.get_rect(center=space_list_pos['main menu'])
    screen.blit(text_surface, rect)
    menu_buttons_rect['main menu'] = rect


# helper function to determine the route from outside of the engineering quad buildings to a specified study "space"
# takes one input
# returns an ordered array of the recommended route (starting from index 0)
def determine_route(space):
    # duffield atrium and ECE lounge accesible without crossing through any other area; short circuit
    if (space == 'Duffield atrium'): return ['Duffield']
    if (space == 'ECE lounge'): return ['Phillips']

    # short circuit: if duffield, phillips, and upson are all congested, skip them and go straight to upson/rhodes
    if ('Rhodes' in space) and (space_list['Duffield atrium'] == 3 and space_list['ECE lounge'] == 3):
        return ["Rhodes"]

    # otherwise, determine route through buildings
    # the values, even in strings, can be compared with operators such as >, <, >=, etc
    route = []

    # start from duffield atrium if it is green or yellow level, otherwise start at phillips
    # but if phillips is red then go through upson instead
    route_start = ""
    if (int(space_list['Duffield atrium']) <= 2):
        route_start = "Duffield"
    elif (int(space_list['ECE lounge']) <=2):
        route_start = "Phillips"
    else: route_start = "Upson"
    route.append(route_start)

    # if in rhodes, need to go through upson; if in upson, of course go through upson
    route.append('Upson')
    # if in upson, end here
    if (space == 'CIS lounge') or ('Upson' in space):
        #print (route)
        return route
    
    # if nothing above and code comes all the way down here, the space must be in rhodes
    route.append('Rhodes')
    #print("THE ROUTE IS ",route)
    return route
 
# show map & draw route on it - specialized version of updateSurfaceAndRect
def draw_route_on_map(route):
    # between each label, draw the line
    # do this first so that the line appears behind the label
    for i in range(len(route) - 1):
        line_start_pos = tuple(map(int,congestion_menu[route[i]]))
        line_end_pos = tuple(map(int,congestion_menu[route[i+1]]))
        pygame.draw.line(screen, BLACK, line_start_pos, line_end_pos, 5) # increase the last parameter for thicker line

    # for each item in the route, draw label on the map
    for i in range(len(route)):
        my_text = route[i]
        displayString = my_text
        box_color = SKYBLUE if (i != (len(route)-1)) else RED
        text_surface = create_text_box(displayString, WHITE, box_color, 50, 50)
        text_pos = congestion_menu[my_text]
        rect = text_surface.get_rect(center=tuple(map(int,text_pos)))
        screen.blit(text_surface, rect)
        #menu_buttons_rect[my_text] = rect
    

    # draw main menu button
    text_surface = create_text_box('main menu', WHITE, SKYBLUE, 50, 50)
    rect = text_surface.get_rect(center=tuple(map(int,congestion_menu['main menu'])))
    screen.blit(text_surface, rect)
    congestion_buttons_rect['main menu'] = rect

# def drawDashboard(hall_name):
#     mrtg_lst = mult_webscraper.convert_df_to_graph_lst(congestion_df, dashboard_hall)
#     count = 1
#     for images in mrtg_lst:
#     #     # draw mrtg graphs
#         response = requests.get("http://mrtg.cit.cornell.edu/switch/WorkDir/"+images)
#         file = open("sample_image.png", "wb")
#         file.write(response.content)
#         file.close()

#         print(images + " are here!")
#         mrtg_graph = pygame.image.load("./img/duffield2-5400.120-day.png")
#         # screen.blit(mrtg_graph, (int(screen_width/8), int(screen_height/8) * count))
#         # draw tables
        

# general all-purpose use helper function to update screen
# OPTIONAL input argument: route, so that we can continue to use updateScreen as a generalized function
#   while also correctly updating the route 
def updateScreen(route=[]):
    screen.fill(BLACK)
    if menu_level == 1: # main menu
        updateSurfaceAndRect(menu_buttons)
        
    elif menu_level ==2: # congestion map
        determine_congestion_level()
        # map is shown properly on monitor
        campus_map = pygame.image.load('./img/map.png')
        campus_map = pygame.transform.scale(campus_map, (screen_width, screen_height))
        screen.blit(campus_map, (0,0))
        updateSurfaceAndRect(congestion_menu)
    elif menu_level == 3: # study spaces
        determine_congestion_level()
        recommended_spaces_list = updateSurfaceAndRect_StudySpace()
        #updateSurfaceAndRect_StudySpace()
    
    elif menu_level == 4:
        # mrtg_graph = pygame.image.load("./img/duffield2-5400.120-day.png")
        # screen.blit(mrtg_graph, (int(screen_width/8), int(screen_height/8)))
        # dashboard_hall = my_text
        mrtg_lst = mult_webscraper.convert_df_to_graph_lst(congestion_df, dashboard_hall)
        print(mrtg_lst)
        count = 1
        count_2 = 1
        text_surface = create_text_box(dashboard_hall.upper(), YELLOW, YELLOW, 10, 10)
        screen.blit(text_surface, (int(screen_width/2)-30,int(screen_height/8-50)))
        df = congestion_df_dashboard
        for index, images in enumerate(mrtg_lst):
            # draw mrtg graphs
            print("INDEX ISSSSS: "index)
            mrtg_graph = pygame.image.load("./img/"+images)
            text_surface = create_text_box(images.replace("png",''), SKYBLUE, SKYBLUE, 10, 10)
            text_info = create_text_box(mult_webscraper.in_out_by_hall(df, images, index-1) , SKYBLUE, SKYBLUE, 10, 10)
            
            if count >= 6:
                screen.blit(mrtg_graph, (int(screen_width/8)*4+30, int(screen_height/6) * count_2))
                screen.blit(text_surface, (int(screen_width/8)*4+30, int(screen_height/6) * count_2-30))
                count_2+=1
            else:
                screen.blit(mrtg_graph, (int(screen_width/8), int(screen_height/6) * count))
                screen.blit(text_surface, (int(screen_width/8), int(screen_height/6) * count-30))
                screen.blit(text_info, (int(screen_width/2), int(screen_height/6) * count))

            count+=1



        # if dashboard_hall == ''
        # df = mult_webscraper.in_out_by_hall(df,dashboard_hall)

    elif menu_level == 5:
        # map is shown properly on monitor
        campus_map = pygame.image.load('./img/map.png')
        campus_map = pygame.transform.scale(campus_map, (screen_width, screen_height))
        screen.blit(campus_map, (0,0))
        #TODO: determine_route(space) needs to be stuck in somewhere based on what's clicked in menu level 3
        # until then, here's a placeholder variable for route
        # route = determine_route(my_text)
        draw_route_on_map(route)
        
    pygame.display.flip()


###NOTE: DON'T USE THIS BECAUSE WHEN updateScreen() IS CALLED IN THE WHILE LOOP, IT DOESN'T EVEN HIT THIS AT ALL
# # specialized updateScreen because it needs route passed into it...
# def updateRouteScreen(route):
#     screen.fill(BLACK)
#     if menu_level == 5: # study space route
#         # map is shown properly on monitor
#         campus_map = pygame.image.load('./img/map.png')
#         campus_map = pygame.transform.scale(campus_map, (1400, 1080))
#         screen.blit(campus_map, (250,0))
#         #TODO: determine_route(space) needs to be stuck in somewhere based on what's clicked in menu level 3
#         # until then, here's a placeholder variable for route
#         #route = []
#         #draw_route_on_map(route)
#     pygame.display.flip()

updateScreen()

while (time.time() < end_time):
    time.sleep(0.2)
    #stop_button()

    # update the congestion level data in script every five minutes
    if time.time() > update_time:
        congestion_data = update_congestion_data()
        determine_congestion_level()
        if menu_level == 2:
            updateScreen() # this function also detects menu_level so it'll be able to update the surface & rect properly
        update_time = time.time() + 300
        # after 10 minutes, the congestion map crashed?

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
                        # print('hit congestion map')
                        menu_level = 2
                        # tempText = my_text
                        # menu_buttons['main menu'] = menu_buttons.pop('congestion map')
                        # newText = my_text
                        # newRect = rect
                        updateScreen()
                        break
                    if (my_text=='main menu'): 
                        # if (menu_level == 2):
                        #     menu_buttons['congestion map'] = menu_buttons.pop('main menu')
                        # elif (menu_level == 3):
                        #     menu_buttons['study spaces'] = menu_buttons.pop('main menu')
                        menu_level = 1
                        # tempText = my_text
                        # #pygame.draw.circle(screen, (139,0,0), (160,120),35,0)
                        # newText = my_text
                        # newRect = rect
                        updateScreen()
                        break
                    if (my_text=='study spaces'):
                        menu_level = 3
                        # tempText = my_text
                        # menu_buttons['main menu'] = menu_buttons.pop('study spaces')
                        # newText = my_text
                        # newRect = rect
                        hall_name = my_text.lower()
                        updateScreen()
                        break
                    # congestion map clicked & shows dashboard (menu 2->4)
                    # TODO: check if this works
                    if (my_text in congestion_menu):
                        menu_level = 4
                        dashboard_hall = my_text
                        # mrtg_lst = mult_webscraper.convert_df_to_graph_lst(congestion_df, dashboard_hall)
                        # print(mrtg_lst)
                        # count = 1
                        # for images in mrtg_lst:
                        # #     # draw mrtg graphs
                        #     mrtg_graph = pygame.image.load("./img/"+images)
                        #     screen.blit(mrtg_graph, (int(screen_width/8), int(screen_height/8) * count))
                        #     count+=1
                        # tempText = my_text
                        # menu_buttons['congestion map'] = menu_buttons.pop('dashboard')
                        # newText = my_text
                        # newRect = rect
                        updateScreen()
                        break
                    
                    #TODO: check in lab if this works! it should show a map & draw lines between the recommended route
                    if (my_text in space_list):
                        menu_level = 5
                        # tempText = my_text
                        # menu_buttons['study spaces'] = menu_buttons.pop('main menu')
                        # newText = my_text
                        # newRect = rect
                        #route = determine_route(my_text)
                        #updateScreen(route)
                        updateScreen()
                        break
                    if (my_text=='quit'):
                        sys.exit()
            # del menu_buttons_rect[tempText]
            # menu_buttons_rect[newText] = newRect
    
    # for button presses, when doing "remote control" of the menu
    # if in congestion map, the buttons are top-to-bottom sequential
    if (menu_level == 1):
        if ( not GPIO.input(27) ):
            menu_level = 2 #go to congestion map
            updateScreen()
            # break
        if ( not GPIO.input(23) ):
            menu_level = 3 #go to study spaces
            # hall_name = my_text.lower()
            updateScreen()
            # break

    elif (menu_level == 2):
        if ( not GPIO.input(27) ): # Phillips
            menu_level = 4 #go to dashboard
            # drawDashboard("Phillips")
            dashboard_hall = 'Phillips'
            updateScreen()
            # break
        if ( not GPIO.input(23) ): # Duffield
            menu_level = 4 #go to dashboard
            # drawDashboard("Duffield")
            dashboard_hall = 'Duffield'
            updateScreen()
            # break
        if ( not GPIO.input(22)): # Upson
            menu_level = 4 #go to dashboard
            # drawDashboard("Upson")
            dashboard_hall = 'Upson'
            updateScreen()
            # break
        if ( not GPIO.input(17)): #Rhodes
            menu_level = 4 #go to dashboard
            # drawDashboard("Rhodes")
            dashboard_hall = 'Rhodes'
            updateScreen()
            # break
    elif (menu_level == 3):
        if ( not GPIO.input(27) ):
            route = determine_route(recommended_spaces_list[0])
            menu_level = 5 #go to routing
            updateScreen(route)
            # break
        if ( not GPIO.input(23)):
            route = determine_route(recommended_spaces_list[1])
            menu_level = 5 #go to routing
            updateScreen(route)
            # break
        if ( not GPIO.input(22)):
            route = determine_route(recommended_spaces_list[2])
            menu_level = 5 #go to routing
            updateScreen(route)
            # break
        if ( not GPIO.input(17)):
            route = determine_route(recommended_spaces_list[3])
            menu_level = 5 #go to routing
            updateScreen(route)
            # break
    
    # clicked main menu button
    if ( not GPIO.input(26) ):
        menu_level = 1
        updateScreen()
        # break
    # panic button
    if ( not GPIO.input(13) ):
        pygame.quit()
        sys.exit()
