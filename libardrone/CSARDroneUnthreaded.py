import libardrone
import cv2
from MultiCamShift import *
import time
import threading

class PatternFollow:  ## removed the thread part of this
    def __init__(self):
        self.drone = libardrone.ARDrone(True)
        self.lock = threading.Lock()
        self.runFlag = True
        self.mcs = MultiCamShift(self.drone, self, trackColors = ["pink", "blue"])
        self.mcs.start()
        self.height, self.width, self.depth = self.drone.image_shape #self.mcs.getFrameDims()
        self.cx, self.cy = self.width / 2, self.height / 2
        self.targetRelativeArea = 0.035


    def run(self):
        self.drone.speed = 1
        time.sleep(1)
        self.drone.takeoff()
        time.sleep(2.5)
        runFlag = True
        while runFlag:
            cv2.waitKey(100)
            matchState = self.mcs.getHorzMarkerInfo(outerColor = "pink", centerColor = "blue")
            if matchState != None:
                print("CSARDrone says: matchstate =", matchState)
                self.patternReact(matchState)
                self.drone.hover()
            with self.lock:
                runFlag = self.runFlag
        self.quit()


    def patternReact(self, patternInfo):
        """"""
        # (x,y) is center point of center color
        # relativeArea is how big area of two outer colors together is compared to the whole drone image
        # angle is positive if area of left outer color is smaller than right outer color
        (x, y), relativeArea, angle, _1, _2 = patternInfo

        # Scores made to make hierarchy of "issues" with target in drone's view.
        # Most critical (highest score) is the issue the drone tries to solve by moving
        xScore = abs(x - self.cx) / float(self.cx)

        yScore = abs(y - self.cy) / float(self.cy)

        angleScore = abs(angle / 90)

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

        # If none of the scores are big enough to return any issues with the target in the drone's view to avoid
        # drone constantly trying to fix minute issues
        if bestScore < 0.3:
            return

        # If center color is left/right of drone's view
        if bestName == "xScore":
            if x < self.cx:
                self.drone.move_left()
                print("move_left")
            else:
                self.drone.move_right()
                print("move_right")
            time.sleep(0.10)

        # If one outer color has greater area visible to drone than other (meaning color strip is angled)
        elif bestName == "angleScore":
            if angle > 0.0:
                self.drone.turn_right()
                time.sleep(0.10)
                self.drone.move_left()
                print("adjust angle right")
            else:
                self.drone.turn_left()
                time.sleep(0.10)
                self.drone.move_right()
                print("adjust angle left")
            time.sleep(0.30)

        # If target area does not take up enough area of drone's view (too far away/close-up)
        elif bestName == "areaScore":
            if relativeArea < self.targetRelativeArea:
                self.drone.move_forward()
                print("move_forward")
            else:
                self.drone.move_backward()
                print("move_backward")
            time.sleep(0.45)

        # If center color is too high/low in drone's view
        elif bestName == "yScore":
            # height indexes from the top down
            if y > self.cy:
                self.drone.move_down()
                print("move_down")
            else:
                self.drone.move_up()
                print("move_up")
            time.sleep(0.2)

        # if bestName == "xScore":
        #     if x < self.cx:
        #         self.drone.move_left()
        #         print("move_left")
        #     else:
        #         self.drone.move_right()
        #         print("move_right")
        #     time.sleep(0.09)
        # elif bestName == "angleScore":
        #     if angle > 0.0:
        #         self.drone.move_left()
        #         self.drone.turn_right()
        #         print("adjust angle right")
        #     else:
        #         self.drone.move_right()
        #         self.drone.turn_left()
        #         print("adjust angle left")
        #     time.sleep(0.20)
        # elif bestName == "areaScore":
        #     if relativeArea < self.targetRelativeArea:
        #         self.drone.move_forward()
        #         print("move_forward")
        #     else:
        #         self.drone.move_backward()
        #     print("move_backward")
        #     time.sleep(0.45)
        # elif bestName == "yScore":
        #     # height indexes from the top down
        #     if y > self.cy:
        #         self.drone.move_down()
        #         print("move_down")
        #     else:
        #         self.drone.move_up()
        #         print("move_up")
        #     time.sleep(0.2)


    def quit(self):
        with self.lock:
            self.runFlag = False
        self.drone.land()
        print("Quitting Drone")
        time.sleep(2)
        self.drone.reset()
        self.drone.halt()
        cv2.destroyAllWindows()
        self.mcs.stop()


PatternFollow().run()
