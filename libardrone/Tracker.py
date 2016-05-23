import numpy as np
import cv2
import math

class Tracker(object):
    def __init__(self, frameDims, track_window, found):
        """"""
        self.track_window = track_window
        self.found = found

        #Threshold Values
        self.trackThreshold = 70
        self.splitThreshold = 60

        self.checkEvery = 3
        self.sinceLastCheck = 0
        self.width, self.height = frameDims
        self.bproj = np.zeros((self.height, self.width), float)


    def update(self, bproj):
        """Updates the camshift trackwindow for this particular object"""
        self.bproj = bproj.copy()
        split = False

        #Checks the accuracy of the tracker every self.checkEvery times
        if self.sinceLastCheck >= self.checkEvery:
            self.accuracyCheck()
            # if self.found:
            # cv2.imshow("FOUND", self.bproj)
            split = self.needsSplitting() and self.found
            self.sinceLastCheck = 0

        term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

        window = list(self.track_window)
        for i, num in enumerate(self.track_window): # prevents track windows from having negative dimensions
            if num < 1:
                window[i] = 1
        c,r,w,h = window
        self.track_rect, self.track_window = cv2.CamShift(bproj, (c,r,w,h), term_crit)

        c,r,w,h = self.track_window

        #Erases the area around the track_window inside the backprojection so the next tracker doesn't see it
        bproj[int(math.ceil(0.95 * (r))):int(math.ceil(1.05 * (r + h))), int(math.ceil(0.95 * (c))):int(math.ceil(1.05 * (c + w)))] = 0
        self.sinceLastCheck += 1
        return self.track_rect, bproj, split


    def backProjAverage(self, window):
        """Gets an average of the values in the backprojection"""
        c,r,w,h = window
        npArray = self.bproj[r:r+h, c:c+w]
        npSum = np.sum(npArray)
        area = (w+1)*(h+1)

        return npSum / area


    def accuracyCheck(self):
        """Makes sure that the track window has a backProjAverage of at least self.trackThreshold"""
        fWidth, fHeight = self.bproj.shape
        if self.backProjAverage(self.track_window) <= self.trackThreshold:
            self.track_window = (0,0,fWidth,fHeight)
            self.found = False
        else:
            self.found = True


    def needsSplitting(self):
        """Checks to see if the tracker should be split"""
        #checks in the middle of the track window to see if that area is the right color
        center = self.getCenter()
        c,r,w,h = self.track_window
        box_width, box_height = (w // 5), (h // 5)
        box_window = (center[0] - box_width // 2), (center[1] - box_height // 2), box_width, box_height
        return self.backProjAverage(box_window) < self.splitThreshold


    def getMatchLevel(self):
        """Returns a normalized score for the accuracy of the track window"""
        return self.backProjAverage(self.track_window) / 255.0

    def getTrackWindow(self):
        return self.track_window

    def getArea(self):
        c,r,w,h = self.track_window
        return w*h

    def getCenter(self):
        c,r,w,h = self.track_window
        return (c + w // 2), (r + h // 2)

    def hasFound(self):
        return self.found
