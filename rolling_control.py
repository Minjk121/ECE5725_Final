import time
import RPi.GPIO as GPIO
import sys
import pygame
from pygame.locals import * # for event MOUSE variables
import os

## motor setup
GPIO.setmode(GPIO.BCM)
# left servo
GPIO.setup(16, GPIO.OUT) # GPIO16 for PWMA
GPIO.setup(20, GPIO.OUT) # GPIO20 for AI1
GPIO.setup(21, GPIO.OUT) # GPIO21 for AI2
# right servo
GPIO.setup(12, GPIO.OUT) # GPIO10 for PWMB
GPIO.setup(5, GPIO.OUT) # GPIO5 for BI1
GPIO.setup(6, GPIO.OUT) # GPIO6 for BI2
# buttons :(
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down = GPIO.PUD_UP)


freq = 50 # 50 Hertz
STOPPED = 0 # dutycycle 
HALFSPEED = 50 # 50% duty cycle
FULLSPEED = 100 # 100% duty cycle

p_a = GPIO.PWM(16, freq)
p_b = GPIO.PWM(12, freq)
p_a.start(STOPPED)
p_b.start(STOPPED)


## pygame/piTFT setup
os.putenv('SDL_VIDEODRIVER','fbcon') 
os.putenv('SDL_FBDEV','/dev/fb1')

# comment these out when running on monitor
# track mouse clicks on piTFT
os.putenv('SDL_MOUSEDRV','TSLIB')
os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')

def servo_command(servo_num, direction, speed):
    if (servo_num == 'LEFT'): # left servo
        if (speed == 0): # if speed = 0, stop, then don't look at direction
            GPIO.output(20, GPIO.LOW)
            GPIO.output(21, GPIO.LOW) 
        elif(direction == 'CW'):
            GPIO.output(20, GPIO.HIGH)
            GPIO.output(21, GPIO.LOW)
            p_a.ChangeDutyCycle(speed)
        elif(direction == 'CCW'):
            GPIO.output(20, GPIO.LOW)
            GPIO.output(21, GPIO.HIGH)
            p_a.ChangeDutyCycle(speed)
    if (servo_num == 'RIGHT'): # right servo
        if (speed == 0): # if speed = 0, stop, then don't look at direction
            GPIO.output(5, GPIO.LOW)
            GPIO.output(6, GPIO.LOW)
        elif(direction == 'CW'):
            GPIO.output(5, GPIO.HIGH)
            GPIO.output(6, GPIO.LOW)
            p_b.ChangeDutyCycle(speed)
        elif(direction == 'CCW'):
            GPIO.output(5, GPIO.LOW)
            GPIO.output(6, GPIO.HIGH)
            p_b.ChangeDutyCycle(speed)


# initialize everything as stopped
GPIO.output(20, GPIO.LOW)
GPIO.output(21, GPIO.LOW)
GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.LOW)

# for piTFT finding t0
t0 = time.time()
end_time = t0 + 30

# initialize pygame for piTFT 
pygame.init()
pygame.mouse.set_visible(False)
WHITE=255,255,255
BLACK=0,0,0
screen=pygame.display.set_mode((320,240))
my_font = pygame.font.Font(None, 25)
# these store the screen coordinates of the logs
left_motor_log_disp={'left history':(70,40),'top':(50,80),'mid':(50,100),'bottom':(50,120)}
right_motor_log_disp={'right history':(250,40),'top':(230,80),'mid':(230,100),'bottom':(230,120)}
buttons={'stop':(160,120),'quit':(270,200)}

# the actual motor logs
left_motor_log = ['STOP','0','STOP','0','STOP','0']
right_motor_log = ['STOP','0','STOP','0','STOP','0']


screen.fill(BLACK) # erase the workspace
buttons_rect={}
started_motor = True

def updateSurfaceAndRect(buttons,left):
    for my_text, text_pos in buttons.items():
        if (my_text =='top' and left):
            displayString = left_motor_log[0]+', '+left_motor_log[1]
        elif (my_text == 'mid' and left):
            displayString = left_motor_log[2]+', '+left_motor_log[3]
        elif (my_text == 'bottom' and left):
            displayString = left_motor_log[4]+', '+left_motor_log[5]

        elif (my_text=='top' and not left):
            displayString = right_motor_log[0]+', '+right_motor_log[1]

        elif (my_text=='mid' and not left):
            displayString = right_motor_log[2]+', '+right_motor_log[3]
        elif (my_text=='bottom' and not left):
            displayString = right_motor_log[4]+', '+right_motor_log[5]
        else:
            displayString = my_text
        text_surface = my_font.render(displayString, True, WHITE)
        rect = text_surface.get_rect(center=text_pos)
        screen.blit(text_surface,rect)
        if (len(buttons) < 4):
            buttons_rect[my_text] = rect


def updateScreen():
    screen.fill(BLACK)
    if (not started_motor):
        # green button
        pygame.draw.circle(screen, (0,128,0),(160,120),35,0)
    else:
        # red button
        pygame.draw.circle(screen, (139,0,0), (160,120),35,0)
    updateSurfaceAndRect(buttons,False)
    updateSurfaceAndRect(left_motor_log_disp,True)
    updateSurfaceAndRect(right_motor_log_disp,False)
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
            for (my_text, rect) in buttons_rect.items():
                if (rect.collidepoint(pos)):
                    if (my_text=='stop'):
                        # print('hit stop')
                        leftSavedState = left_motor_log[4]
                        rightSavedState = right_motor_log[4]
                        servo_command('LEFT','CW',STOPPED)
                        servo_command('RIGHT','CW',STOPPED)
                        tempText = my_text
                        started_motor = False
                        buttons['resume'] = buttons.pop('stop')
                        newText = my_text
                        #newRect = rect
                        newRect = rect.inflate(20, 20)
                        pygame.draw.circle(screen, (0,128,0),(160,120),35,0)
                        updateScreen()
                        break
                    if (my_text=='resume'):
                        started_motor = True
                        tempText = my_text
                        buttons['stop'] = buttons.pop('resume')
                        newText = my_text
                        #newRect = rect
                        newRect = rect.inflate(20, 20)
                        pygame.draw.circle(screen, (139,0,0), (160,120),35,0)
                        left_motor_log.pop(0)
                        left_motor_log.pop(0)
                        left_motor_log.append(leftSavedState)
                        left_motor_log.append(str(int(time.time()-t0)))
                        right_motor_log.pop(0)
                        right_motor_log.pop(0)
                        right_motor_log.append(rightSavedState)
                        right_motor_log.append(str(int(time.time()-t0)))
                        servo_command('LEFT',leftSavedState,HALFSPEED)
                        servo_command('RIGHT',rightSavedState,HALFSPEED)
                        updateScreen()
                        break
                    if (my_text=='quit'):
                        sys.exit()
            del buttons_rect[tempText]
            buttons_rect[newText] = newRect
    if ( not GPIO.input(27) and started_motor):
        print("button 27 pressed: left servo clockwise")
        servo_command('LEFT','CW',HALFSPEED)
        left_motor_log.pop(0)
        left_motor_log.pop(0)
        left_motor_log.append('CW')
        left_motor_log.append(str(int(time.time()-t0)))
    elif ( not GPIO.input(23) and started_motor):
        print("button 23 pressed: left servo stop")
        servo_command('LEFT','CW',STOPPED)
        left_motor_log.pop(0)
        left_motor_log.pop(0)
        left_motor_log.append('STOP')
        left_motor_log.append(str(int(time.time()-t0)))
    elif ( not GPIO.input(22) and started_motor):
        print("button 22 pressed: left servo counter clockwise")
        servo_command('LEFT','CCW',HALFSPEED)
        left_motor_log.pop(0)
        left_motor_log.pop(0)
        left_motor_log.append('CCW')
        left_motor_log.append(str(int(time.time()-t0)))
    elif ( not GPIO.input(17) and started_motor):
        print("button 17 pressed: right servo clockwise")
        servo_command('RIGHT','CW',HALFSPEED)
        right_motor_log.pop(0)
        right_motor_log.pop(0)
        right_motor_log.append('CW')
        right_motor_log.append(str(int(time.time()-t0)))
    elif ( not GPIO.input(26) and started_motor):
        print("button 26 pressed: right servo stopped")
        servo_command('RIGHT','CW',STOPPED)
        right_motor_log.pop(0)
        right_motor_log.pop(0)
        right_motor_log.append('STOP')
        right_motor_log.append(str(int(time.time()-t0)))
    elif ( not GPIO.input(13) and started_motor):
        print("button 13 pressed: right servo counter clockwise")
        servo_command('RIGHT','CCW',HALFSPEED)
        right_motor_log.pop(0)
        right_motor_log.pop(0)
        right_motor_log.append('CCW')
        right_motor_log.append(str(int(time.time()-t0)))

    updateScreen()

p_a.stop()
p_b.stop()
GPIO.cleanup()
