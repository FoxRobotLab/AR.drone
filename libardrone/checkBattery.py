import libardrone
import cv2
import time

class CheckDrone:
    def __init__(self):
        """Sets up a drone object Binds the keypress and release to callback functions"""
        self.drone = None
        self.main = cv2.namedWindow("Drone View")

        self.drone = libardrone.ARDrone(True)
        print("Drone initialized")
        print("\n q for quit \n spacebar for takeoff/land \n b for battery level check \n AWSD directional control \n i for altitude info")
        self.inAir = False
        self.quitting = False


    def go(self):
        """Loops until user types q"""
        while True:
            self.showCamera()
            self.userKeyResponse()
            self.checkAltitude()
            if self.quitting:
                cv2.destroyAllWindows()
                break


    def userKeyResponse(self):
        """Checks for user input and responds to it."""
        key = cv2.waitKey(20)
        if key == -1:
            return
        key = chr(key % 255)
        if key in {'q', 'Q'}:
            print("Quitting")
            self.drone.land()
            time.sleep(2)
            self.quitting = True
        elif key == ' ':
            if self.inAir:
                print("Landing")
                self.drone.land()
                self.inAir = False
            else:
                print("Taking off")
                self.drone.takeoff()
                self.inAir = True
        elif key in {'b', 'B'}:
            navData = self.drone.get_navdata()
            print("Battery level is", navData[0]['battery'])
            print(navData)
        elif key in {'x', 'x'}:
            if self.inAir:
                self.drone.move_up()
                time.sleep(0.3)
                self.drone.hover()
        elif key in {'c', 'C'}:
            if self.inAir:
                self.drone.move_down()
                time.sleep(0.3)
                self.drone.hover()
        elif key in {'w', 'W'}:
            if self.inAir:
                self.drone.move_forward()
                time.sleep(0.3)
                self.drone.hover()
        elif key in {'s', 'S'}:
            if self.inAir:
                self.drone.move_backward()
                time.sleep(0.3)
                self.drone.hover()
        elif key in {'a', 'A'}:
            if self.inAir:
                self.drone.move_left()
                time.sleep(0.3)
                self.drone.hover()
        elif key in {'d', 'D'}:
            if self.inAir:
                self.drone.move_right()
                time.sleep(0.3)
                self.drone.hover()
        elif key in {'i', 'I'}:
            navData = self.drone.get_navdata()
            print("Altitude is ", navData[0]["altitude"])



    def checkAltitude(self):
        navData = self.drone.get_navdata()
        alt = navData[0]["altitude"]
        print("Altitude is ", alt)
        if alt > 1700:
            self.drone.move_down()
            time.sleep(.45)
            self.drone.hover()
            print("Drone is too high")
        if alt < 300:
            self.drone.move_up()
            time.sleep(.45)
            self.drone.hover()
            print("Drone is too low")


    def showCamera(self):
        imgArray = self.drone.get_image()
        rc, gc, bc = cv2.split(imgArray)
        imgArray = cv2.merge((bc, gc, rc))
        self.displayImage = imgArray[:, :, :]
        cv2.imshow("Drone View", self.displayImage)


def runDrone():
    """This runs the drone program"""
    foo = CheckDrone()
    foo.go()


runDrone()
