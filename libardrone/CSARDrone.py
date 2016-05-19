import libardrone
import cv2
from MultiCamShift import *
import time
import threading

class PatternFollow(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.drone = libardrone.ARDrone(True)
        self.lock = threading.Lock()
        self.runFlag = True
        self.mcs = MultiCamShift(self.drone, self, trackColors = ["green", "blue"])
        self.mcs.start()
        self.width, self.height = self.mcs.getFrameDims()
        self.cx, self.cy = self.width / 2, self.height / 2
        self.targetRelativeArea = 0.035


    def run(self):
        # self.drone.speed = 1
        # time.sleep(1)
        # self.drone.takeoff()
        # time.sleep(2.5)
        runFlag = True
        while runFlag:
            time.sleep(1)
            matchState = self.mcs.getHorzMarkerInfo(outerColor = "green", centerColor = "blue")
            if matchState != None:
                print("CSARDrone says: matchstate =", matchState)
                self.patternReact(matchState)
                # self.drone.hover()
            with self.lock:
                runFlag = self.runFlag


    def patternReact(self, patternInfo):
        """"""
        (x, y), relativeArea, angle = patternInfo
        
        xDiff = abs(x - self.cx)
        xScore = xDiff / (self.width / 2.0) * (7 / 6.0) # because the edges of the frame are cut off in MCS
        
        yDiff = abs(y - self.cy)
        yScore = yDiff / (self.height / 2.0) * (5 / 4.0)
        
        angleScore = abs(angle / 90) * 1.5
        
        areaScore = abs(max((1 - relativeArea / self.targetRelativeArea), -1))

        print("Angle", angle)
        print("________________________")
        print("CSARDrone")
        print("xScore =", xScore)
        print("yScore =", yScore)
        print("angleScore =", angleScore)
        print("areaScore =", areaScore)

        scores = [("xScore", xScore), ("areaScore", areaScore), ("angleScore", angleScore), ("yScore", yScore)]
        
        bestName, bestScore = scores[0]
        
        for score in scores:
            name, num = score
            if num > bestScore:
                bestName, bestScore = score
                
        if bestScore < 0.4:
            return
        
        if bestName == "xScore":
            if x < self.cx:
                self.drone.turn_left()
                print("turn_left")
            else:
                self.drone.turn_right()
                print("turn_right")
            time.sleep(0.09)
        elif bestName == "angleScore":
            if angle > 0.0:
                self.drone.move_left()
                print("move_left")
            else:
                self.drone.move_right()
                print("move_right")
            time.sleep(0.43)
        elif bestName == "areaScore":
            if relativeArea < self.targetRelativeArea:
                self.drone.move_forward()
                print("move_forward")
            else:
                self.drone.move_backward()
                print("move_backward")
            time.sleep(0.45)
        elif bestName == "yScore":
            #height indexes from the top down
            if y > self.cy:
                self.drone.move_down()
                print("move_down")
            else:
                self.drone.move_up()
                print("move_up")
            time.sleep(0.2)


    #def patternReact(self, patternInfo):
        #(x, y), relativeArea, angle = patternInfo
        #if abs(x - self.cx) > self.width / 9:
            #if x < self.cx:
                #self.drone.turn_left()
                #print "turn_left"
            #else:
                #self.drone.turn_right()
                #print "turn_right"
            #time.sleep(0.07)
        #elif abs(angle) > 16:
            #if angle > 0.0:
                #self.drone.move_left()
                #print "move_left"
            #else:
                #self.drone.move_right()
                #print "move_right"
            #time.sleep(0.3)
        #elif abs(relativeArea -  self.targetRelativeArea) > 0.015:
            #if relativeArea < self.targetRelativeArea:
                #self.drone.move_forward()
                #print "move_forward"
            #else:
                #self.drone.move_backward()
                #print "move_backward"
            #time.sleep(0.4)
        #elif abs(y - self.cy) > self.height / 6:
            ##height indexes from the top down
            #if y > self.cy:
                #self.drone.move_down()
                #print "move_down"
            #else:
                #self.drone.move_up()
                #print "move_up"
            #time.sleep(0.2)

    def quit(self):
        with self.lock:
            self.runFlag = False
        self.drone.land()
        print("Quitting Drone")
        time.sleep(2)
        self.drone.reset()
        self.mcs.stop()
        

PatternFollow().start()
