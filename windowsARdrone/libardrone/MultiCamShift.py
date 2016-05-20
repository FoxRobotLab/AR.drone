import numpy as np
import cv2
import threading
import math
import itertools
from operator import itemgetter
from datetime import datetime

from TargetScanner import *

class MultiCamShift(threading.Thread):
    
    def __init__(self, drone, parentProgram, trackColors = ["red", "green", "blue", "violet", "indigo", "pink"]):
        """Creates the cam shift thread and sets up scanners for all objects listed in 'self.toScanFor'"""
        threading.Thread.__init__(self)
        self.toScanFor = trackColors
        self.scanners = {}
        self.lock = threading.Lock()
        self.locationAndArea = {}
        self.drone = drone
        self.running = True
        self.parent = parentProgram
        self.currFrame = None
        self.patternInfo = None
        
        self.fHeight, self.fWidth, self.fDepth = self.drone.image_shape

        for colorName in self.toScanFor:
            self.scanners[colorName] = TargetScanner(colorName, (self.fWidth, self.fHeight))

        # determines how close together in the y direction the colors of a horizontal pattern must be.
        self.horzPatternYSpacing = self.fHeight / 8.0

        # determines how uniform the distances between the colors in a pattern must be
        self.horzPatternXRatio = 2
        
        #for the AR.Drone program: ignores colors that are at within this distance to the edge of the screen
        self.horzMarkerBorder = self.fWidth / 14
        self.vertMarkerBorder = self.fHeight / 10
        
        
    def run(self):
        """Will run the tracking program on the video from vid_src."""
        running = True
        cv2.namedWindow("Drone Camera")
        while running:
            image = self.drone.image.copy()
            red, green, blue = cv2.split(image)
            image = cv2.merge((blue, green, red))
            self.currFrame = image
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
        print("Quitting MCS")
        cv2.destroyWindow("Drone Camera")
        cv2.waitKey(10)
        

    def stop(self):
        with self.lock:
            self.running = False

    def displayPattern(self):
        (x, y), relativeArea, angle, upperLeft, lowerRight = self.patternInfo
        cv2.rectangle(self.currFrame, upperLeft, lowerRight, (0, 0, 225), 2)
        #cv2.imshow("Drone Camera", self.currFrame)

    def update(self):
        """Updates the trackers with the given image."""
        hsv_image = cv2.cvtColor(self.currFrame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_image, np.array((0., 60., 45.)), np.array((255., 255., 255.)))
        objects = {}        
        for colorName in self.scanners:
            scanner = self.scanners[colorName]
            image = scanner.scan(self.currFrame, hsv_image, mask)
            objects[colorName] = scanner.getTrackingInfo()    
        if self.patternInfo is not None:
            self.displayPattern()    
        with self.lock:
            self.locationAndArea = objects
            self.currFrame = image            
        return image


    def getObjectsOfColor(self, color_name):
        """Returns a list of objects locations and area of all identified objects of type 'color_name'."""
        with self.lock:
            locationAndArea = self.locationAndArea[color_name]
        return locationAndArea


    def getHorzMarkerInfo(self, outerColor, centerColor):
        """For the AR.Drone program: returns info about the marker"""
        with self.lock:
            outerData = self.locationAndArea[outerColor][:]
            centerData = self.locationAndArea[centerColor][:]
        if len(outerData) < 2 or len(centerData) == 0:
            self.patternInfo = None
            return None
        top1CenterByScore = sorted(centerData, key=itemgetter(1), reverse = True)[0]
        top2OuterByScore = sorted(outerData, key=itemgetter(1), reverse = True)[0:2]
        left, right = sorted(top2OuterByScore)
        (lx, ly, lw, lh), lScore = left
        (cx, cy, cw, ch), cScore = top1CenterByScore
        (rx, ry, rw, rh), rScore = right
        if not (lx <= cx and cx <= rx):
            self.patternInfo = None
            return None
        #Ensures neither the left or the right Pattern is too close to the edge of the screen
        if not (self.horzMarkerBorder <= lx and rx <= self.fWidth - self.horzMarkerBorder) or \
            not (self.vertMarkerBorder <= ly and ly <= self.fHeight - self.vertMarkerBorder) or \
            not (self.vertMarkerBorder <= ry and ry <= self.fHeight - self.vertMarkerBorder):
            self.patternInfo = None
            return None
        lArea = float(lw * lh)
        rArea = float(rw * rh)
        if lArea <= rArea:
            angle = 90.0 * (1 - lArea / rArea)
        else:
            angle = -90.0 * (1 - rArea / lArea)
        relativeArea = (lArea + rArea) / (self.fWidth * self.fHeight)

        self.patternInfo = (cx, cy), relativeArea, angle, (lx - lw/2, ly - lh/2), (rx + rw/2, ry + rh/2)
        return self.patternInfo
        #this code should be able to be cleaned up so you just return self.patternInfo


    def checkXCoords(self, xCoords):
        """Checks to see if the x distances are somewhat consistent (Should be close to evenly spaced)"""
        xCoords = sorted(xCoords)
        dXs = xCoords[1] - xCoords[0], xCoords[2] - xCoords[1]
        if max(dXs) / (min(dXs) + 1) < self.horzPatternXRatio:
            return True
        return False


    def checkYCoords(self, yCoords):
        """Checks to see if the y coords are close together"""
        yCoords = sorted(yCoords)
        if yCoords[2] - yCoords[0] <= self.horzPatternYSpacing:
            return True
        return False

    def getFrameDims(self):
            """Returns the the dimensions and depth of the camera frame"""
            return self.fWidth, self.fHeight


    def getFrameCenter(self):
            """Returns the center coordinates of the camera frame"""
            return self.fWidth/2, self.fHeight/2

























