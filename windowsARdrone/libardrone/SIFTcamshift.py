import numpy as np
import cv2
import threading
from datetime import datetime
import os
from droneImageSift import initRefs, findImage


class SIFTcamshift(threading.Thread):
    
    def __init__(self, drone, parentProgram):
        """Creates the cam shift thread and sets up scanners for all objects listed in 'self.toScanFor'"""
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.locationAndArea = {}
        self.drone = drone
        self.running = True
        self.parent = parentProgram
        
        self.frame = None
        self.track_window = None
        self.hist = None
        self.rect = None
        self.hist = None
        
        self.fHeight, self.fWidth, self.fDepth = self.drone.image_shape

        
    def run(self):
        """Will run the tracking program on the video from vid_src."""
        running = True
        cv2.namedWindow("Drone Camera")
        while running:
            image = self.drone.image.copy()
            if image is not None:
                red, green, blue = cv2.split(image)
                image = cv2.merge((blue, green, red))
                self.frame = image
                key = chr(cv2.waitKey(33) & 255)
                if key == 't':
                    time = datetime.now().strftime('%Y-%m-%d-%H%M%S')
                    filename = "cap-" + time + ".jpg"
                    path = ".." + os.path.join(os.sep, "res", "captures", filename)
                    print(path)
                    cv2.imwrite(path, image)
                    print("Image Saved")
                elif key == 'q' or key == ' ':
                    self.parent.quit()
                frame = self.update()
                cv2.imshow("Drone Camera", frame)
            with self.lock:
                running = self.running
        print("Quitting Camshift")
        cv2.destroyWindow("Drone Camera")
        cv2.waitKey(10)
        
    def stop(self):
        with self.lock:
            self.running = False

    def displayPattern(self):
        (x, y), relativeArea, angle, upperLeft, lowerRight = self.patternInfo
        cv2.rectangle(self.frame, upperLeft, lowerRight, (0, 0, 225), 2)
        #cv2.imshow("Drone Camera", self.currFrame)

    def update(self):
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)    # convert to HSV
        mask = cv2.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))   # eliminate low and high saturation and value values
        
        vis1 = self.frame.copy()
        track_window = self.track_window

        if track_window is None or track_window[0] < 1 or track_window[1] < 1 or track_window[2] < 1 or track_window[3] < 1:
            self.track_window = None #just so if it is negative, 0, it's easy for other things to tell that there's nothing detected
            itemsSought = ['hatch', 'exit']
            properties = initRefs(itemsSought)
            rect = findImage(vis1, properties, itemsSought, 0)
            if rect is not None: #if findImage didn't return anything, just pass and try again
                x, y, w, h = rect
                #print("rect is", rect)
                cv2.rectangle(vis1,(x,y),(x+w,y+h),(0,255,0),2)
                
                self.track_window = (x, y, w, h)
                print("track window", self.track_window)
    
                hsv_roi = hsv[y:h+y, x:w+x]             # access the currently selected region and make a histogram of its hue 
                mask_roi = mask[y:h+y, x:w+x]
    
                """trying to take only a subsection of the image, in case the whole
                select by contour thing got some extra - just an experiment to see
                if it improved camshift's accuracy - by appearances, no."""
#                hsv_roi = hsv[y+(h/4):(3*h/2)+y, x+(w/4):(3*w/2)+x]             # access the currently selected region and make a histogram of its hue 
#                mask_roi = mask[y+(h/4):(3*h/2)+y, x+(w/4):(3*w/2)+x]
    
                hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
                cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
                self.hist = hist.reshape(-1)
                #print(hist)
            
        else: #from camShiftDemo
            prob = cv2.calcBackProject([hsv], [0], self.hist, [0, 180], 1)
            prob &= mask
            
            #opening removes the remanants in the background
            kernel = np.ones((8,8),np.uint8)
            prob = cv2.morphologyEx(prob, cv2.MORPH_OPEN, kernel)
            
            #thresholding to black adn white removes the grey areas of noise opening left
            ret,prob = cv2.threshold(prob,127,255,cv2.THRESH_BINARY)
            
            #cv2.imshow("Mask", prob)
            white = cv2.countNonZero(prob)
            #print("white", white)
            
            #if there's any remnants remaining, don't look at them - only run if there's a Significant thing
            if white > 1000:
                term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 1)
                track_box, self.track_window = cv2.CamShift(prob, self.track_window, term_crit)
                try:
                    cv2.ellipse(vis1, track_box, (0, 0, 255), 2)
                except:
                    print track_box
            else:
                self.track_window = None
        
        return vis1

    def getCurrTrackbox(self):
        return self.track_window

    def getFrameDims(self):
            """Returns the the dimensions and depth of the camera frame"""
            return self.fWidth, self.fHeight


    def getFrameCenter(self):
            """Returns the center coordinates of the camera frame"""
            return self.fWidth/2, self.fHeight/2

























