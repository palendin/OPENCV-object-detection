import cv2 as cv
import pyautogui
from time import sleep, time
from threading import Thread, Lock
from OPENCV_windowcapture import WindowCapture
import win32gui, win32ui, win32con
from math import sqrt

class BotState:
    INITIALIZING = 0 #data structure known as emum
    SEARCHING = 1
    MOVING = 2
    ATTACKING = 3
    BACKTRACKING = 4
 

class RSBot:

    #constants
    INITIALIZING_SECONDS = 6
    ATTACKING_SECONDS = 8
    MOVEMENT_STOPPED_THRESHOLD = 0.8
    IGNORE_RADIUS = 50 #ignoring objects within 50 pixels

    #thread properties
    stopped = True
    lock = None

    #properties
    state = None
    targets = []
    screenshot = None
    timestamp = None
    movement_screenshot = None #previous screenshot
    game_window = None #actual game window
    w = 0
    h = 0
    border_pixel = 0
    titlebar_pixel = 0
    click_history = []

    def __init__(self, game_window, window_size):
        #create thread object
        self.lock = Lock()

        #start the bot and mark the time
        self.state = BotState.INITIALIZING #set property to the property of another class
        self.timestamp = time()
        self.game_window = game_window #initialize game window for get_screen_position method
        self.w = window_size[0] 
        self.h = window_size[1] #this w x h screen will have greyish borders which we dont really want
        self.border_pixel = 10
        self.titlebar_pixel = 30

    def have_stopped_moving(self):
        #store a screenshot to cmpare
        if self.movement_screenshot is None:
            self.movement_screenshot = self.screenshot.copy()
            return False #if False, it will wait before looping again in the MOVING state. Then in the next loop, previous screenshot is saved.
        #compare two screenshots

        result = cv.matchTemplate(self.screenshot, self.movement_screenshot, cv.TM_CCOEFF_NORMED)
        #because two images are same size, there is only 1 result
        similarity = result[0][0]
        print('similary value:{}'.format(similarity))
        if similarity >= self.MOVEMENT_STOPPED_THRESHOLD:
            print('character stopped moving')
            return True

        else:
            self.movement_screenshot = self.screenshot.copy()
            return False

    def click_next_target(self):
        #order by distance
        targets = self.targets_ordered_by_distance(self.targets)
        target_i = 0
        found_cow = False
        #loop
        while not found_cow and target_i < len(targets):

            #if script is stopped, exit
            if self.stopped:
                break
            
            #get closest target
            target_pos = targets[target_i]
            print('target is x:{}'.format(target_pos))
            screen_x, screen_y = self.get_screen_position(target_pos)
            print('move to x:{} y:{}'.format(screen_x, screen_y))

            pyautogui.moveTo(x=screen_x,y=screen_y)
            sleep(0.1) #sleep to wait for tooltip

            #verify target
            if self.confirm_tooltip(target_pos):
                found_cow = True
                pyautogui.click()
                self.click_history.append(target_pos)

            #end loop
            #if no target found, end loop return false on click_next_target()
            #click target and return true on click_next_target()
            target_i +=1
        
        return found_cow
    
    def confirm_tooltip(self, target_position): #need to detect text here to make sure target is correct
        target_position = target_position
        return True
    
    def click_backtrack(self):
        #takes the last saved item in the click history list and put it in the last_click list as the first item, and so on. so it reverse the list
        last_click = self.click_history.pop()
        #backtracking clickpoints
        my_pos = (self.w/2, self.h/2)
        mirror_x = my_pos[0] - (last_click[0] - my_pos[0]) #in parathesis = how many pixels i need to move
        mirror_y = my_pos[0] - (last_click[0] - my_pos[0])

        #convert to relative pos on the game screen
        screen_x, screen_y = self.get_screen_position(mirror_x,mirror_y)
        
        pyautogui.moveTo(x=screen_x,y=screen_y)
        sleep(0.5)
        pyautogui.click


    def get_screen_position(self, pos): 
        hwnd_target = win32gui.FindWindow(None,self.game_window) #continuously find where the game window is to calculate relative position
        window_position = win32gui.GetWindowRect(hwnd_target)
        winx = window_position[0] 
        winy = window_position[1]
        targetx =  winx + pos[0] + self.border_pixel #relative position
        targety =  winy + pos[1] + self.titlebar_pixel
        return (targetx, targety) #(pos[0] + self.offset_x, pos[1] + self.offset_y)

    def targets_ordered_by_distance(self, targets):
        my_pos = (self.w/2, self.h/2)
        def pythagorean(pos):
            return sqrt((my_pos[0] - pos[0])**2+(my_pos[1]-pos[1])**2)
        targets.sort(key=pythagorean) #sort the input target clickpoints from least to greatest (default) by the pythagorean rule (key)
        
        targets = [t for t in targets if pythagorean(t) > self.IGNORE_RADIUS]
        return targets

    def update_targets(self, targets):
        self.lock.acquire()
        self.targets = targets
        self.lock.release()
    
    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()
    
    def start(self):
        self.stopped = False #first indicate false before start thread for run()
        t = Thread(target=self.run)
        t.start()
    
    def stop(self):
        self.stopped = True

    #main logic controller
    def run(self):
        while not self.stopped:
            if self.state == BotState.INITIALIZING:
                if time() > self.timestamp + self.INITIALIZING_SECONDS: #compare current time vs current time + some seconds
                    self.lock.acquire()
                    self.state = BotState.SEARCHING #switch over to another state
                    self.lock.release()
                
            if self.state == BotState.SEARCHING:
                #confirm the target clickpoint and click it
                success = self.click_next_target()
                if not success:
                    success = self.click_next_target()

                if success:
                    self.lock.acquire()
                    self.state = BotState.MOVING
                    self.lock.release()
                elif len(self.click_history) > 0:
                    self.click_backtrack()
                    self.lock.acquire()
                    self.state = BotState.BACKTRACKING
                    self.lock.release()
                else:
                    pass #stay and keep searching
            
            elif self.state == BotState.MOVING or self.state == BotState.BACKTRACKING:
                #compare previous to current screenshot see if we stop moving
                if not self.have_stopped_moving():
                    sleep(0.5)
                else:
                    #swittch state and reset timer if attacking. search again if backtracking
                    self.lock.acquire()
                    if self.state == BotState.BACKTRACKING:
                        self.state == BotState.SEARCHING
                    if self.state == BotState.MOVING:
                        self.timestamp = time()
                        self.state = BotState.ATTACKING
                    self.lock.release()
            
            elif self.state == BotState.ATTACKING:
                #check_health()
                #check_target_health(), if 0, then go to search state
                if time() > self.timestamp + RSBot.ATTACKING_SECONDS:
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()