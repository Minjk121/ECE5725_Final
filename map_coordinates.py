import RPi.GPIO as GPIO
import time
import sys

import pygame
from pygame.locals import * # for event MOUSE variables
import os

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

os.putenv('SDL_VIDEODRIVER','fbcon') #display piTFT
os.putenv('SDL_FBDEV','/dev/fb0')
# os.putenv('SDL_MOUSEDRV','TSLIB') # track mouse clicks on piTFT
# os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')

pygame.init()
#pygame.mouse.set_visible(False)
WHITE=255,255,255
BLACK=0,0,0

# find the monitor resolution
infoObject = pygame.display.Info()
print(infoObject.current_w, infoObject.current_h)
screen=pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
# screen=pygame.display.set_mode((1920,1080))
 
# screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN)
my_font=pygame.font.Font(None, 25)
my_buttons={'quit':(1800,900),'touch at ':(200,200)}
screen.fill(BLACK) # erase the workspace
end_time = time.time()+30

image = pygame.image.load('./img/map.png')
image = pygame.transform.scale(image, (1400, 1080))
screen.blit(image, (250,0))

my_buttons_rect={}
for my_text, text_pos in my_buttons.items():
    text_surface=my_font.render(my_text, True, WHITE)
    rect=text_surface.get_rect(center=text_pos)
    if (my_text=='touch at '):
        rect = pygame.Rect(0,0,1920,1080)
    screen.blit(text_surface, rect)
    my_buttons_rect [my_text] = rect # save rect for 'my-text' button

pygame.display.flip()

while True:
    time.sleep(0.2)
    if ( not GPIO.input(17)): # quit button 17
        print("bailing out")
        sys.exit()
    # if (time.time() > end_time): # timeout timer
    #     print("TIMEOUT")
    #     sys.exit()

    for event in pygame.event.get():
        if(event.type is MOUSEBUTTONDOWN):
            pos=pygame.mouse.get_pos()
        # output is shown only when the mouse button goes up (mouse input inverted)
        elif(event.type is MOUSEBUTTONUP):
            pos=pygame.mouse.get_pos()
            x,y=pos # set coordinates x and y
            for (my_text, rect) in my_buttons_rect.items():
                if (rect.collidepoint(pos)):
                    if(my_text=='quit'): # when quit is pressed, exit system
                        print("quitting")
                        sys.exit()
                    else: # show coordinates x and y
                        my_text = 'touch at '+str(x)+', '+str(y)
                        print(my_text)
                        text_surface = my_font.render(my_text,True,WHITE)
                        quit_text_surface = my_font.render('quit',True,WHITE)
                        screen.fill(BLACK)
                        screen.blit(text_surface,rect)
                        screen.blit(quit_text_surface,my_buttons_rect['quit'])
                        screen.blit(image, (250,0))
                        pygame.display.flip()
                        pygame.display.update([rect,my_buttons_rect['quit']])
        # screen.blit(image, (250,0))

