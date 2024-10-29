#goal is to filter out images we are not interested in before sending the image of interest to matchtemplate() to get better identification
#create a slider gui trackbar to see a range of HSV values for the image filter
#refine the find() function into smaller functions so its clearer when we add in color filters into the image detection


import cv2 as cv #cv is just another reference
import numpy as np #python library for working with linear algbra such as arrays, matrix, fourier transform. NumPy = numerical python
#from pathlib import Path
#import os
#from hsvfilter import HsvFilter

class Vision:
    # properties
    object_image = None
    object_w = 0
    object_h = 0
    method = None
    TRACKBAR_WINDOW = "Trackbars" #name for trackbar window gui

    def __init__(self, object_path, method = cv.TM_CCOEFF_NORMED): #think about what do we want to pass in when we start the vision class
        if object_path: #avoid error if None
            self.object_image = cv.imread(object_path, cv.IMREAD_UNCHANGED) #(file location, read mode)
            self.object_w = self.object_image.shape[1] #access x value of the image
            self.object_h = self.object_image.shape[0]
            self.method = method #self.variable is class property

    #background_image will be coming from windowcapture
    #no longer need object_image in find() because we declared that in the constructor, that will save as a property of a class
    def find(self, background_image, threshold):

        #this returns a multi dim array, each number represent confidence score of the match. Can use debugger to look at the array in row by col format, or dim(y,x)
        result = cv.matchTemplate(self.object_image, background_image, self.method) 
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

        #setting threshold of the match
        locations = np.where(result >= threshold) #returns the indices of elements in an input array where the given condition is satisfied. 
        #note that in result, all values are <= 1, so np.where() returns the "position" of a result in row by column, or (y,x) format
        #print(locations) #here it returns 2 array that contans all matches to the threshold, first array contains y values and second contains x. This also contains additional info which isnt needed
        
        #alternatively, this is a better way to output the matched location
        locations = list(zip(*locations[::-1])) # ::-1 just reverse the location tuples so y x become x,y; * unpacks the list so a 2D array becomes 2x1D array, zip make new lists where it takes all the items in a single index and combines them together            
        print(locations)

        # group rectangles expect a list of [x,y,w,h] format, where x,y is the location of the upper left corner.
        rectangles = [] #first create a list of rectangles
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.object_w, self.object_h] #get the x y value in each location tuple
            rectangles.append(rect)
            rectangles.append(rect) #append again to get repeated overlapping results for the groupRectangle to eliminate. Now at threshold of 0.7, you will have 4 squares instead of 1 square.
        print('ungroup rectangles are,', rectangles)

        #group rectangles of similar location
        rectangles, weights = cv.groupRectangles(rectangles, 1, eps = 1) #2nd param is groupthreshold, if its 0, it wont group at all. 3rd parameter: larger the value, rectangle further away will be grouped together
        print('grouped rectangles are,', rectangles)

        #note: rectangle result output requires at least 2 overlap locations, if there isnt, it will just throw the nonoverlap location out. A trick is to append the rectangles list twice. 
        return rectangles

    def get_click_points(self, rectangles):
        points = []

        #loop through the locations and draw rectangle around it. and then create points for mouse to click
        for (x,y,w,h) in rectangles: #another way of accessing elements in the rectangle array, by unpacking
            #find center position of the rectangle
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))    
        
        return points

    def draw_rectangles(self, Background_Img, rectangles):
        line_color = (0,255,0)
        line_type = cv.LINE_4
        line_thickness = 2
        for (x,y,w,h) in rectangles:
            top_left = (x,y)
            bottom_right = (x + w), (y + h) #since max_loc is a tuple, top_left(0) and (1) access the x and y component in the max_loc
            cv.rectangle(Background_Img, top_left, bottom_right, line_color, line_thickness, line_type)
        
        return Background_Img


    def draw_crosshairs(self, background_image, points):
        marker_color = (255,0,255)
        marker_type = cv.MARKER_CROSS
        for (center_x, center_y) in points:
            cv.drawMarker(background_image, (center_x, center_y), marker_color, marker_type,markerSize=40,thickness=2)

        return background_image

    #points = findClickPositions(object_path,background_image, 0.7, debug_mode = 'rectangles') #this will return none if return points isnt define in the function. Alternatively, print() inside the function
    #print('debug mode gives you the points:', points)
'''
    def init_control_gui(self):
        #create a gui window
        cv.namedWindow(self.TRACKBAR_WINDOW, cv.WINDOW_NORMAL) #namedwindow creates a window name, 'window_normal' enabling resize window
        cv.resizeWindow(self.TRACKBAR_WINDOW, 350, 700)

        def nothing(position):  #everytime we call createTrackbar, it needs a function (call back function) parameter.
            pass
            #Anytime the trackbar is changed, it runs that function. We wont use this, we will just look up trackbar positions when we need it. 
            #nothing function is created above for the createtrackbar so satisfies the argument

        #openCV scale for HSV is H: 0-179, S: 0-255, V:0-255
        #create trackbars with sliders 
        cv.createTrackbar('H_min', self.TRACKBAR_WINDOW, 0, 179, nothing) #the string is the name of the trackbar
        cv.createTrackbar('S_min', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('V_min', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('H_max', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('S_max', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('V_max', self.TRACKBAR_WINDOW, 0, 255, nothing)
     
        #create trackbars for increasing/decreasing saturation and value
        cv.createTrackbar('S_add', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('S_sub', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('V_add', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('V_sub', self.TRACKBAR_WINDOW, 0, 255, nothing)

        #set default value for Max HSV Trackbars. The slider will be set at a defined value
        cv.setTrackbarPos('H_max', self.TRACKBAR_WINDOW, 179)
        cv.setTrackbarPos('S_max', self.TRACKBAR_WINDOW, 255)
        cv.setTrackbarPos('V_max', self.TRACKBAR_WINDOW, 255)
     
      
    #returns a HSV filter object baSed on the control GUI values
    def get_hsv_filter_from_controls(self):
        #initialize an object from Hsv filter class (object = class(argument)) and get current position ("values") of the specified trackbar
        hsv_filter = HsvFilter()
       
        hsv_filter.Hmin =  cv.getTrackbarPos('H_min', self.TRACKBAR_WINDOW) #calling the hsv_filter property (Hmin, Smin, etc) on the hsv_filter object
        hsv_filter.Smin =  cv.getTrackbarPos('S_min', self.TRACKBAR_WINDOW)
        hsv_filter.Vmin =  cv.getTrackbarPos('V_min', self.TRACKBAR_WINDOW)
        hsv_filter.Hmax =  cv.getTrackbarPos('H_max', self.TRACKBAR_WINDOW)
        hsv_filter.Smax =  cv.getTrackbarPos('S_max', self.TRACKBAR_WINDOW)
        hsv_filter.Vmax =  cv.getTrackbarPos('V_max', self.TRACKBAR_WINDOW)
        hsv_filter.Sadd =  cv.getTrackbarPos('S_add', self.TRACKBAR_WINDOW)
        hsv_filter.Subb =  cv.getTrackbarPos('S_sub', self.TRACKBAR_WINDOW)
        hsv_filter.Vadd =  cv.getTrackbarPos('V_add', self.TRACKBAR_WINDOW)
        hsv_filter.Vsub =  cv.getTrackbarPos('V_sub', self.TRACKBAR_WINDOW)

        return hsv_filter #return hsvfilter object with all the trackbar positions
    
    #now we can apply filter and return the image
    def apply_hsv_filter(self, original_image, hsv_filter = None): #hsv_filter = None: if no pre-determined hsvfilter, the control trackbar GUI will be used
        
        #first convert image to HSV format
        hsv_image = cv.cvtColor(original_image, cv.COLOR_BGR2HSV)

        if not hsv_filter:
            hsv_filter = self.get_hsv_filter_from_controls() #self also needed when calling other functions/methods
        
        #create numpy array object with min and max HSV values 
        lower = np.array([hsv_filter.Hmin, hsv_filter.Smin, hsv_filter.Vmin]) #access the properties from hsvfilter class()
        upper = np.array([hsv_filter.Hmax, hsv_filter.Smax, hsv_filter.Vmax])

        #apply the threshold using input HSV value, and lower and upper HSV numbers. It will check if array elements lies between the elements of other 2 arrays. if its in range, returns 1, if not, returns 0. so it will be a black (0) and white (1) image
        mask = cv.inRange(hsv, lower, upper) 
        result = cv.bitwise_and(hsv, hsv, mask = mask) #calculate the element bit-wise junction of 2 array or array/scalar
      
        #convert back to BGR for imshow()
        img = 

        return img

        cv.imshow()

#mask and cv.bitwise_and explanation:
#general usage is that you want to get a subset of an image defined by another image known as the "mask". by applying this mask to the image, calculation is performed 
#so the function returns 1 at every pixel where there is a 1 for both mask and image, else returns 0

#similarly, bitwise_not is the opposite. it turns 1 to 0, and 0 to 1.
#bitwise_or returns 1 whenever either mask or image has 1s, else return 0s
'''