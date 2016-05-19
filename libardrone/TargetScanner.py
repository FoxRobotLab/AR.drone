import numpy as np
import cv2
import os

from Tracker import *

class TargetScanner(object):
    def __init__(self, object_name, frame_dims):
        """Creates the object and generates the histogram for the object to be tracked (object_name)."""
        self.object_name = object_name
        self.frameDims = frame_dims
        self.fWidth, self.fHeight = frame_dims
        #Full window, useful for reseting track windows
        self.full_track_window = (0,0,self.fWidth,self.fHeight)

        fullStr = object_name + ".jpg"
        path = ".." + os.path.join(os.sep, "res", "images", fullStr)

        try:
            self.object_image = cv2.imread(path)
        except:
            print(object_name + " image could not be read")

        self.averageColor = self.calcAverageColor()        
        
        object_hsv = cv2.cvtColor(self.object_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(object_hsv, np.array((0., 50., 30.)), np.array((255., 255., 255.)))
        self.hist = cv2.calcHist([object_hsv], [0], mask, [16], [0,255])
        cv2.normalize(self.hist, self.hist, 0, 255, cv2.NORM_MINMAX)
        
        #Contains trackers for objects already found by the searcher
        self.tracking = []
        
        #Tracker that is looking for new objects
        self.searcher = Tracker(self.frameDims, self.full_track_window, False)
        
    
    def calcAverageColor(self):
            """Calculates the average color of the object to be tracked."""
            imgWidth, imgHeight, imgDepth = self.object_image.shape
            area = imgWidth * imgHeight
            return (int(np.sum(self.object_image[:,:,0]) / area),
                    int(np.sum(self.object_image[:,:,1]) / area),
                    int(np.sum(self.object_image[:,:,2]) / area))     
        
        
    def scan(self, frame, hsv_frame, mask):
        """Updates all the of trackers for identified objects and updates the searcher which is looking for new objects."""
        bproj = cv2.calcBackProject([hsv_frame], [0], self.hist, [0,255], 1)        
        bproj &= mask        
        for index, tracker in enumerate(self.tracking):
            original_bproj = bproj.copy()
            box, bproj, split = tracker.update(bproj)
            coords, dims, theta = box
            w,h = dims
            if split:
                self.splitTracker(tracker)
                del self.tracking[index]
                bproj = original_bproj
            if tracker.hasFound() and w > 0 and h > 0:
                cv2.ellipse(frame, box, self.averageColor, 2)
            else:
                del self.tracking[index]                
        box, bproj, split = self.searcher.update(bproj.copy())        
        if split:
            self.splitTracker(self.searcher)
            self.searcher = Tracker(self.frameDims, self.full_track_window, found = False)
        if self.searcher.hasFound(): # If searcher finds an object, start tracking that object and make a new searcher
            self.tracking.append(self.searcher)
            self.searcher = Tracker(self.frameDims, self.full_track_window, found = False)            
        return frame

    
    def getTrackingInfo(self):
        """Returns the tracking info ((x, y,width, height), matchScore) about all the currently identified objects."""
        info = []
        for tracker in self.tracking:
            if tracker.hasFound():
                c,r,w,h = tracker.getTrackWindow()
                x,y = tracker.getCenter()
                score = tracker.getMatchLevel()
                info.append(((x,y,w,h), score))
        return info
        
    
    def splitTracker(self, tracker):
        """Using the info from tracker, it splits the tracker into 4 new trackers with each having a trackbox of the 4 quadrants of the original tracker."""
        #Useful if tracked objects pass by each other
        c,r,w,h = tracker.getTrackWindow()        
        w1 = w // 2
        w2 = w - w1
        h1 = h // 2
        h2 = h - h1        
        for newBox in [(c, r, w1, h1), (c+w1+1, r, w2, h1), (c, r+h1+1, w1, h2), (c+w1+1, r+h1+1, w2, h2)]:
            self.tracking.append(Tracker(self.frameDims, newBox, True))


