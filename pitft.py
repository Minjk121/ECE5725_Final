# Display "start" and "quit" buttons on piTFT with screen coordinates
import RPi.GPIO as GPIO
import time
from datetime import date
import sys

import pygame
from pygame.locals import * # for event MOUSE variables
import os

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

os.putenv('SDL_VIDEODRIVER','fbcon') #display piTFT
os.putenv('SDL_FBDEV','/dev/fb1')
# os.putenv('SDL_MOUSEDRV','TSLIB') # track mouse clicks on piTFT
# os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')

pygame.init()
# pygame.mouse.set_visible(False)
WHITE=255,255,255
BLACK=0,0,0
screen=pygame.display.set_mode((320,240))
my_font=pygame.font.Font(None, 25)

my_buttons={'start':(60,200),'quit':(120,200),'touch at ':(100,100)} # set three buttons on screen
menus = {'top':(230,40),'mid':(230,80),'bottom':(230,120)}
# cur_time = time_now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")


screen.fill(BLACK) # erase the workspace
# end_time = time.time()+30
size = width, height = 320,240
speed = [3,3]
speed2 = [1,1]

my_buttons_rect={}

# set screen coordinate functionality
def updateButtons():
    for my_text, text_pos in my_buttons.items():
        text_surface=my_font.render(my_text, True, WHITE)
        rect=text_surface.get_rect(center=text_pos)
        if (my_text=='touch at '):
            rect = pygame.Rect(0,0,320,240)
        screen.blit(text_surface, rect)
        my_buttons_rect [my_text] = rect # save rect for 'my-text' button

updateButtons()
pygame.display.flip()

ballStart = False
time.sleep(0.2)
while True:
    time.sleep(0.002)
    if ( not GPIO.input(17)): # set GPIO 17 as exit button
        print("bailing out")
        sys.exit()
    # if (time.time() > end_time): # set 30-second timeout timer
    #     print("TIMEOUT")
        sys.exit()
    if (ballStart): # collide two balls
        ballrect = ballrect.move(speed)
        ballrect2 = ballrect2.move(speed2)
        if ballrect.left < 0 or ballrect.right > width:
            speed[0] = -speed[0]
        if ballrect2.left < 0 or ballrect2.right > width:
            speed2[0] = -speed2[0]
        if ballrect.top < 0 or ballrect.bottom > height:
            speed[1] = -speed[1]
        if ballrect2.top < 0 or ballrect2.bottom > height:
            speed2[1] = -speed2[1]
        if ballrect.colliderect(ballrect2):
            s = speed
            speed = speed2
            speed2 = s
        screen.fill(BLACK)
        screen.blit(ball, ballrect)
        screen.blit(ball2, ballrect2)
        for (my_text, rect) in my_buttons_rect.items():
            text_surface = my_font.render(my_text, True, WHITE)
            screen.blit(text_surface, rect)

        pygame.display.flip()
    for event in pygame.event.get():
        if(event.type is MOUSEBUTTONDOWN):
            pos=pygame.mouse.get_pos()
        elif(event.type is MOUSEBUTTONUP):
            pos=pygame.mouse.get_pos()
            x,y=pos
            for (my_text, rect) in my_buttons_rect.items():
                if (rect.collidepoint(pos)):
                    if(my_text=='quit'): # when "quit" button is pushed, exit system   
                        print("quitting")
                        sys.exit()
                    elif(my_text=='start'): # when "start" button is pushed, start the colliding animation
                        ballStart = True
                        ball = pygame.image.load("soccer_ball.png")
                        ball = pygame.transform.scale(ball, (100,100))
                        ball2 = pygame.image.load("volleyball_ball.png")
                        ball2 = pygame.transform.scale(ball2, (50,50))
                        ballrect = ball.get_rect()
                        ballrect = ballrect.inflate(-5,-5)
                        ballrect2 = ball2.get_rect()
                        ballrect2 = ballrect2.inflate(-20,-20)
                        ballrect = ballrect.move([125,125])
                    else: # display coordinates of the touched surface
                        tempText = my_text
                        my_text= 'touch at '+str(x)+', '+str(y)
                        print(my_text)
                        newText = my_text
                        newRect = rect
                        text_surface = my_font.render(my_text,True,WHITE)
                        quit_text_surface = my_font.render('quit',True,WHITE)
                        start_text_surface = my_font.render('start',True,WHITE)        
                        screen.fill(BLACK)
                        screen.blit(text_surface,rect)
                        screen.blit(quit_text_surface,my_buttons_rect['quit'])
                        screen.blit(start_text_surface,my_buttons_rect['start'])       
                        if (ballStart):
                            screen.blit(ball, ballrect)
                            screen.blit(ball2, ballrect2)
                        pygame.display.flip()
                        pygame.display.update([rect,my_buttons_rect['quit']])
            del my_buttons_rect[tempText]
            my_buttons_rect[newText] = newRect