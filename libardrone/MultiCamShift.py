import numpy as np
import cv2
import threading
import math
import itertools
from operator import itemgetter
from datetime import datetime
import time

from TargetScanner import *

class MultiCamShift(threading.Thread):

    def __init__(self, drone, parentProgram, trackColors = ["red", "green", "blue", "violet", "indigo"]):
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
        self.i = 0
        self.land = 0

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
            x = cv2.waitKey(33)
            if x != -1:
                print("User override")
                key = chr(x & 255)
                if key == 't':
                    time = datetime.now().strftime('%Y-%m-%d-%H%M%S')
                    filename = "cap-" + time + ".jpg"
                    path = ".." + os.path.join(os.sep, "res", "captures", filename)
                    print(path)
                    cv2.imwrite(path, image)
                    print("Image Saved")
                elif key in {'i', 'I'}:
                    self.drone.move_up()
                    time.sleep(0.3)
                    self.drone.hover()
                elif key in {'k', 'K'}:
                    self.drone.move_down()
                    time.sleep(0.3)
                    self.drone.hover()
                elif key in {'j', 'J'}:
                    self.drone.turn_left()
                    time.sleep(0.3)
                    self.drone.hover()
                elif key in {'l', 'L'}:
                    self.drone.turn_right()
                    time.sleep(0.3)
                    self.drone.hover()
                elif key in {'w', 'W'}:
                    self.drone.move_forward()
                    time.sleep(0.3)
                    self.drone.hover()
                elif key in {'s', 'S'}:
                    self.drone.move_backward()
                    time.sleep(0.3)
                    self.drone.hover()
                elif key in {'a', 'A'}:
                    self.drone.move_left()
                    time.sleep(0.3)
                    self.drone.hover()
                elif key in {'d', 'D'}:
                    self.drone.move_right()
                    time.sleep(0.3)
                    self.drone.hover()
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
        # blurImage = cv2.GaussianBlur(self.currFrame, (5, 5), 0)
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
        cv2.rectangle(self.currFrame, (160, 90), (480, 270), (0,225), 1)          #approximated target box for testing
        return image


    def getObjectsOfColor(self, color_name):
        """Returns a list of objects locations and area of all identified objects of type 'color_name'."""
        with self.lock:
            locationAndArea = self.locationAndArea[color_name]
        return locationAndArea


    def getHorzMarkerInfo(self, outerColor, centerColor):
        """For the AR.Drone program: returns info about the marker"""
        self.i = self.i + 1
        if self.i > 75:
            print("No pattern found")
            self.drone.turn_left()
            time.sleep(0.05)
            self.drone.hover()
            navData = self.drone.get_navdata()
            print("Battery level is", navData[0]['battery'])
            self.i = 0
        if self.land > 1000:
            self.drone.land()
            self.parent.quit()
        with self.lock:
            outerData = self.locationAndArea[outerColor][:]
            centerData = self.locationAndArea[centerColor][:]
        if len(outerData) < 2 or len(centerData) == 0:
            self.patternInfo = None
            return None

        """Checks to see if the edges of two objects have similar x-coords. Pass it i = 1 to check the 
        left side of the center object (against right side of outer) or i = -1 to check the right side."""
        def checkIfXclose(i, center, outer):
            (ox, oy, ow, oh), oScore = outer
            (cx, cy, cw, ch), cScore = center

            diff = abs((ox + i*ow) - (cx - i*cw))
            #print("X diff is", diff )

            if diff < 150:
                return True
            return False

        def checkIfYclose(center, left, right):
            return abs(center[0][1] - left[0][1]) < 150 and abs(center[0][1] - right[0][1]) < 150

        """remember that items in centerData and outerData are of form ((x, y, w, h), score), where
        (x, y) is the center of the item, w and h are the width and height respectively, and score
        is supposed to be the back projection of the item against the sample it's being compared to,
        but is actually 0.0 for some unknown reason."""
        def findTriad(centerData, outerData):
            for center in centerData:
                leftObjects = []
                rightObjects = []
                #finds which blocks are directly to the left and right of the center block
                for outer in outerData:
                    if checkIfXclose(1, center, outer):
                        leftObjects.append(outer)
                    elif checkIfXclose(-1, center, outer):
                        rightObjects.append(outer)
                #if there are blocks to the right and left, see if any are also close in y coords
                if leftObjects and rightObjects:
                    for left in leftObjects:
                        for right in rightObjects:
                            if checkIfYclose(center, left, right):
                                return center, left, right

        triad = findTriad(centerData, outerData)
        if triad is None:
            return None
        else:
            center, left, right = triad


        (lx, ly, lw, lh), lScore = left
        (cx, cy, cw, ch), cScore = center
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

    def getFrameDims(self):
        """Returns the the dimensions and depth of the camera frame"""
        return self.fWidth, self.fHeight


    def getFrameCenter(self):
        """Returns the center coordinates of the camera frame"""
        return self.fWidth/2, self.fHeight/2


























