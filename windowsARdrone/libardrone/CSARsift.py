import libardrone
import cv2
from SIFTcamshift import *
import time
import threading

class PatternFollow:  ## removed the thread part of this
    def __init__(self):
        self.drone = libardrone.ARDrone(True)
        self.lock = threading.Lock()
        self.runFlag = True
        self.scs = SIFTcamshift(self.drone, self)
        self.scs.start()
        self.width, self.height = self.scs.getFrameDims()
        self.cx, self.cy = self.width / 2, self.height / 2
        self.targetRelativeArea = 0.38


    def run(self):
        self.drone.speed = 1
        time.sleep(1)
        self.drone.takeoff()
        time.sleep(2.5)
        runFlag = True
        while runFlag:
            x = cv2.waitKey(30)
            if x != -1:
                ch = chr(x & 255)
                if ch == 'q':
                    break
            track_window = self.scs.getCurrTrackbox()
            if track_window != None:
                #print "CSARDrone says: track window =", track_window
                self.patternReact(track_window)
                self.drone.hover()
            with self.lock:
                runFlag = self.runFlag
        self.quit()


    def patternReact(self, track_window):
        """"""
        # (x,y) is center point of center color
        # relativeArea is how big area of two outer colors together is compared to the whole drone image

        x, y, wp, hp = track_window
        w = wp + x
        h = hp + y
        frameW, frameH = self.scs.getFrameDims()
        relativeArea = (w*h)/float(frameW*frameH)
        #print("(w*h)",  w*h, "(frameW*frameH)", frameW*frameH)

        # Scores made to make hierarchy of "issues" with target in drone's view.
        # Most critical (highest score) is the issue the drone tries to solve by moving
        xScore = abs(x - self.cx) / float(self.cx)
        yScore = abs(y - self.cy) / float(self.cy)
        #we expect this one to be off in the range of .1, .2, so normalise as such
        areaScore = abs(self.targetRelativeArea - relativeArea) / 0.2

        print("________________________")
        print("xScore =", xScore)
        print("yScore =", yScore)
        print("areaScore =", areaScore)

        scores = [("xScore", xScore), ("areaScore", areaScore), ("yScore", yScore)]

        bestName, bestScore = scores[0]

        for score in scores:
            name, num = score
            if num > bestScore:
                bestName, bestScore = score

        # If none of the scores are big enough to return any issues with the target in the drone's view to avoid
        # drone constantly trying to fix minute issues
        if bestScore < 0.4:
            return

        # If center color is left/right of drone's view
        if bestName == "xScore":
            if x+(w/2) < self.cx:
                self.drone.move_left()
                print("move_left")
            else:
                self.drone.move_right()
                print("move_right")
            time.sleep(0.10)

        # If target area does not take up enough area of drone's view (too far away/close-up)
        elif bestName == "areaScore":
            print("Relative area: ", relativeArea)
            if relativeArea < self.targetRelativeArea - .05:
                self.drone.move_forward()
                print("move_forward")
            elif relativeArea > self.targetRelativeArea + .05:
                self.drone.move_backward()
                print("move_backward")
            time.sleep(0.45)

        # If center color is too high/low in drone's view
        elif bestName == "yScore":
            # height indexes from the top down
            if y+(h/2) > self.cy:
                self.drone.move_down()
                print("move_down")
            else:
                self.drone.move_up()
                print("move_up")
            time.sleep(0.2)


    def quit(self):
        with self.lock:
            self.runFlag = False
        self.drone.land()
        print("Quitting Drone")
        time.sleep(2)
        self.drone.reset()
        self.drone.halt()
        cv2.destroyAllWindows()
        self.scs.stop()


PatternFollow().run()
