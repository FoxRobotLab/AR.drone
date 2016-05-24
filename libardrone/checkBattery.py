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
        print("\n q for quit \n spacebar for takeoff/land \n b for battery level check \n")
        self.inAir = False
        self.quitting = False


    def go(self):
        """Loops until user types q"""
        while True:
            self.showCamera()
            self.userKeyResponse()
            if self.quitting:
                cv2.destroyAllWindows()
                break


    def userKeyResponse(self):
        """Checks for user input and responds to it."""
        key = cv2.waitKey(20)
        if key == -1:
            return
        chrKey = chr(key % 255)
        if chrKey in {'q', 'Q'}:
            print("Quitting")
            self.drone.land()
            time.sleep(2)
            self.quitting = True
        elif chrKey == ' ':
            if self.inAir:
                print("Landing")
                self.drone.land()
                self.inAir = False
            else:
                print("Taking off")
                self.drone.takeoff()
                self.inAir = True
        elif chrKey in {'b', 'B'}:
            navData = self.drone.get_navdata()
            print("Battery level is", navData[0]['battery'])


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
