#creating a windowcapture class

#class analogy: in runescape, all characters created belong to the same class, but each character has different attributes like clothes, armor, weapon.
#so class defines all the abilities of instances of the character
#here, the windowcapture class contains abilities (functions) to find window_name and taking screenshots. each function has properties or known as variables that exists inside a class
import numpy as np
import win32gui, win32ui, win32con
from threading import Thread, Lock

#the goal here is to first specify the window dimensions you want before taking the screenshot
class WindowCapture:

    #threading properties
    stopped = True
    lock = None
    screenshot = None

    #properties: screen width and height, and window handler is needed for get_screenshot function to access these variables
    w = 0
    h = 0
    hwnd = None 
    left = 0
    top = 0
    right = 0
    bottom = 0
    border_pixel = 0
    titlebar_pixel = 0
    offset_x = 0
    offset_y = 0

    #constructor, a method that gets called whenever the Windowcapture class is initialize
    def __init__(self, window_name=None): 
        self.lock = Lock()
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            #put window handler here because we dont need to call this every time it takes a screenshot
            self.hwnd = win32gui.FindWindow(None, window_name)  #can specify name of the window we want anywhere on the screen even if its behind or on another monitor
            if not self.hwnd: #if cant find window
                raise Exception('Window not found: {}'.format(window_name))
        
        #instead of defining a window size, get the actual window size that we want to screenshot
        window_rect = win32gui.GetWindowRect(self.hwnd) #this returns 4 values, x1, y1, x2, y2 of the window with index 0, 1, 2, 3
        self.w = window_rect[2] - window_rect[0] 
        self.h = window_rect[3] - window_rect[1] #this w x h screen will have greyish borders which we dont really want

        #cut off window border and title bar
        self.titlebar_pixel = 30
        self.border_pixel = 10
        self.w = self.w - self.border_pixel*2 #this will only crop out the image from the right and make the actual image narrower
        self.h = self.h - self.titlebar_pixel - self.border_pixel #this will crop out the image from the bottom and make it shorter
        #to crop on the left, we need to move the crop image, which is in the get_screenshot function

        #since the screen is cropped, so we need to define an offset to translate the screenshot position to the actual game position
        #our image is cropped from the right and shifted to the left, so offset needs to translate to to right on actual game position 
        self.offset_x = window_rect[0] + self.border_pixel
        self.offset_y = window_rect[1] + self.titlebar_pixel

    #provide a list of windows that you have opened
    @staticmethod #no need "self" inside this function. can use this function without having any instance (no need to have "None" inside when running this function)
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    def get_screenshot(self): #every function inside a class needs to have "self"
        wDC = win32gui.GetWindowDC(self.hwnd) #retrieves device context (DC) from the. DC is a structure that defines a set of graphic objects and their attributes, basically a place that drawing occurs
        dcObj=win32ui.CreateDCFromHandle(wDC)
        cDC=dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap() #bitmap is mapping from some domain into array bits
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h) #create bitmap. w and h variable are properties of self. This is how to reference the properties inside a function that is part of a class
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.border_pixel, self.titlebar_pixel), win32con.SRCCOPY) # in the parameter dcobj, (x2, y2), it shifts the image capture in the defined window. Positive values will shift the actual image to the left, creating black space on the right

        #save screenshot to bitmap form
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')

        #convert screenshot format for imshow()
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h,self.w,4) #calling the shape/sizes of our capture image, -1 or 4 works for the last value. -1 automatically figure out what value it needs. 4 works because 1920x1080x4 = 8294400 which is the size of the array that needs to be reshaped

        # you HAVE TO delete/release all the DCs created by this, or after taking ~90 images.
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        #additional improvements:
        #drop alpha channel (remove information about transparency) or cv.matchTemplate() will throw an error like this:
            #error: (depth == CV_8U || depth == CV_32F) && type == _templ.type() && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[:,:,:3] #get rid of alpha channel data. note that img[...,:3] works also
        #having alpha channel manipulation will slow FPS

        #make image C_contitguous to avoid errors like "cv2.rectangle(). TypeError: an integer is required (got type tuple)"
        img = np.ascontiguousarray(img) #returns a contiguous array, its an array that has consecutive indexes. For ex: [4,5] has consectuive indexes (0,1)

        return img
    #similar, once we get the imgage screenshot, we will pass this img in a format that python wants to imshow() at the bottom

    #from the offset valuse we defined earlier,
    #we now create a function to translate pixel pos(x,y) on a screenshot to an actual (x,y) position on the screen 
    def get_screen_position(self, pos, game_window): 
        hwnd_target = win32gui.FindWindow(None,game_window)
        window_position = win32gui.GetWindowRect(hwnd_target)
        winx = window_position[0] #since its the same window size, find where the actual window is at (x1,y1) then add the position to the window
        winy = window_position[1]
        targetx = winx + pos[0] + self.border_pixel #relative position
        targety = winy + pos[1] + self.titlebar_pixel
        return (targetx, targety) #(pos[0] + self.offset_x, pos[1] + self.offset_y)

    def start(self):
        self.stopped = False #first indicate false before start thread for run()
        t = Thread(target=self.run)
        t.start()
    
    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            screenshot = self.get_screenshot()
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()




