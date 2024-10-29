#with bot.update(targets), this works fine telling where to click
#but it needs other states to determine what the bot is doing, or even to verify the object is correct before clicking
#this needs different bot methods (states). so depending on the state of the bot, it will only need the certain data for that state. This will speed things up

import cv2 as cv #cv is just another reference
import numpy as np #python library for working with linear algbra such as arrays, matrix, fourier transform. NumPy = numerical python
from pathlib import Path
import os
from time import time
from vision import Vision
#import windowcapture #below is simplified because we can now access the Windowcapture class directly
from OPENCV_windowcapture import WindowCapture
import pyautogui
import win32gui, win32ui, win32con
from threading import Thread
from detection import Detection
from bot import RSBot, BotState

dir = os.path.dirname(os.path.abspath(__file__)) #path of this file
positive_path = os.path.join(dir, 'positive') 
negative_path = os.path.join(dir, 'negative') 
#print(positive_path,negative_path)
train_data = os.path.join(dir, 'cascade')
#WindowCapture.list_window_names() #calling the static function to provide all window names

wincap = WindowCapture('Calculator') #create an object to hold the WindowCapture class. it require 1 argument 'window_name' from the constructor __init__()


#load trained model using detection class
cascade_cow_detector = Detection(os.path.join(train_data,'cascade.xml'))

#for accessing functions in Vision class
vision_cow = Vision(None)

#initialize bot object
bot = RSBot('calculator',(wincap.w,wincap.h)) #initializing with game window for getting screen positions

DEBUG = True

#start thread, where start() will create a thread
wincap.start()
cascade_cow_detector.start()
bot.start()

loop_time = time() #static variable to get the current time
while(True):

    #if no screenshot, dont run code below
    if wincap.screenshot is None:
        continue
    
    #get the screenshot (property) from wincap
    screenshot = wincap.screenshot
    
    #screenshot will be refreshed after each loop. In update(), it triggers run() to obtain rectangles
    cascade_cow_detector.update(screenshot)

    #start -> search -> moving -> action 
    if bot.state == BotState.INITIALIZING:
        targets = vision_cow.get_click_points(cascade_cow_detector.rectangles)
        bot.update_targets(targets)
    elif bot.state == BotState.SEARCHING:
        #when searching, need to know clickpoints, need updated screenshot to verify 
        targets = vision_cow.get_click_points(cascade_cow_detector.rectangles)
        bot.update_targets(targets)
        bot.update_screenshot(screenshot)
    elif bot.state == BotState.MOVING:
        #when moving, need updating screenshot to determine when we have stopped moving
        bot.update_screenshot(screenshot)
    elif bot.state == BotState.ATTACKING:
        #eat if needed
        pass
    if DEBUG: 
        #draw detection results onto screenshot
        detection_image = vision_cow.draw_rectangles(screenshot, cascade_cow_detector.rectangles)
        cv.imshow('matches',detection_image)
    

    #print('current time', time(), 'capture_time', time()-loop_time,'and', 'FPS {}'.format(1/(time()-loop_time))) #time()-loop_time = current time - the previous time stamp
    loop_time = time() #update current timestamp

    key = cv.waitKey(25)
    if key == ord('q'): #wait 1 ms and if q is pressed afterwards, it will close out all windows and break out while loop
        cascade_cow_detector.stop() #stop() stores True into the stopped object, which stops run() method
        wincap.stop()
        bot.stop()
        cv.destroyAllWindows()
        break
    
    #elif key == ord('f'):
    #    cv.imwrite(os.path.join(positive_path,'{}.jpg'.format(loop_time)),screenshot) #write to positive folder. using loop_times as the image name
    #elif key == ord('d'):
    #    cv.imwrite(os.path.join(negative_path,'{}.jpg'.format(loop_time)),screenshot) #write to negative folder


print('Done')

