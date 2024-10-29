import cv2 as cv #cv is just another reference
import numpy as np #python library for working with linear algbra such as arrays, matrix, fourier transform. NumPy = numerical python
from threading import Thread, Lock


class Detection:

    #threading properties
    stopped = True
    lock = None

    #properties
    rectangles = []
    screenshot = None
    cascade = None 

    #load model -> get screenshot -> start thread -> stop thread
    def __init__(self,model_file_path):
        #create a thread lock object when initializing
        self.lock = Lock()
        self.cascade = cv.CascadeClassifier(model_file_path)
    
    def update(self, screenshot): #get screenshot from window capture 
        self.lock.acquire()
        self.screenshot = screenshot #saving the screenshot to this object
        self.lock.release()

    def start(self): #start a thread
        self.stopped = False #first indicate false before start thread for run()
        t = Thread(target=self.run)
        t.start()

    def stop(self): 
        self.stopped = True
   
    def run(self):
        while not self.stopped:
            if not self.screenshot is None:
                #if there is a screenshot, get list of rectangles
                rectangles = self.cascade.detectMultiScale(self.screenshot)
               
                #acquire a lock to lock the thread while updating results
                self.lock.acquire()
                self.rectangles = rectangles #save rectangles to class property
                self.lock.release()

                #if another thread is getting new list of rectangles and this thread is updating the rectangles from previous list, conflict will break the program
                #use lock to prevent this issue by locking the thread, update, and release the thread after updating
