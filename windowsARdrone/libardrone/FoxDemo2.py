import cv2
import libardrone
import time


class ShowImages:
    def __init__(self):
        """Sets up a drone object, and a Tkinter window to display the picture 
        and other things.  Binds the keypress and release to callback functions"""
        self.drone = None
        self.main = cv2.namedWindow("Drone View")

        self.displayText = ""
        self.dispFont = cv2.FONT_HERSHEY_SIMPLEX

        self.drone = libardrone.ARDrone(True)
        print("Drone initialized")
        self.inAir = False
        self.quitting = False


    def go(self):
        """Loops until user types q"""
        while True:
            self.nextPicture()
            self.userKeyResponse()
            if self.quitting:
                cv2.destroyAllWindows()
                self.drone.halt()
                break
            
    def userKeyResponse(self):
        """Checks for user input and responds to it."""
        key = cv2.waitKey(20)
        if key == -1:
            return

        chrKey = chr(key % 255)
        if chrKey in {'q', 'Q'}:
            self.drone.land()
            explanText = "Quitting!"
            time.sleep(2)
            self.quitting = True
        elif chrKey in {'n', 'N'}:
            self.testNextPicture()      
            explanText = "Taking picture"
        elif chrKey in {'r', 'R'}:
            self.drone.land()   
            self.drone.reset()
            explanText = "Resetting drone"
        elif chrKey == ' ':
            if self.inAir:
                self.drone.land()
                explanText = "Landing"
                self.inAir = False
            else:
                self.drone.takeoff()
                explanText = "Taking off"
                self.inAir = True
        elif chrKey in {'i', 'I'}:
            if self.inAir:
                self.drone.move_up()
                time.sleep(0.3)
                self.drone.hover()
            explanText = "Moving up"
        elif chrKey in {'k', 'K'}:
            if self.inAir:
                self.drone.move_down()
                time.sleep(0.3)
                self.drone.hover()
            explanText = "Moving down"
        elif chrKey in {'j', 'J'}:
            if self.inAir:
                self.drone.turn_left()
                time.sleep(0.3)
                self.drone.hover()
            explanText = "Turning left"
        elif chrKey in {'l', 'L'}:
            if self.inAir:
                self.drone.turn_right()
                time.sleep(0.3)
                self.drone.hover()
            explanText = 'Turning right'
        elif chrKey in {'w', 'W'}:
            if self.inAir:
                self.drone.move_forward()
                time.sleep(0.3)
                self.drone.hover()
            explanText = 'Moving forward'
        elif chrKey in {'s', 'S'}:
            if self.inAir:
                self.drone.move_backward()
                time.sleep(0.3)
                self.drone.hover()
            explanText = 'Moving backward'
        elif chrKey in {'a', 'A'}:
            if self.inAir:
                self.drone.move_left()
                time.sleep(0.3)
                self.drone.hover()
            explanText = 'Moving left'
        elif chrKey in {'d', 'D'}:
            if self.inAir:
                self.drone.move_right()
                time.sleep(0.3)
                self.drone.hover()
            explanText = 'Moving right'
        elif chrKey in {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}:
            newSpeed = self.keyToSpeed(chrKey)
            self.drone.speed = newSpeed
            explanText = 'Changing speed to ' + str(newSpeed)
        self.outputResponse(explanText)

    def keyToSpeed(self, key):
        """User enters a speed between 0 and 1, and this converts it
        to the float that is expected, returning the speed float value"""
        if key == '0':
            return 1.0
        else:
            num = int(key)
            return num / 10.0
        
    def outputResponse(self, text):
        """Displays in the window and prints the text it is given"""
        self.displayText = text
        print(text)

 
    def nextPicture(self):
        """Takes a picture from the drone, and converts it to display
        in tkinter.  It reschedules itself to run every second"""
        imgArray = self.drone.image
        #navData = self.drone.get_navdata()
        self.displayImage = imgArray[:,:,:]
        if self.displayText != "":
            cv2.putText(self.displayImage, 
                        self.displayText, 
                        (20, 300),
                        self.dispFont,
                        1,
                        (255, 255, 0))
        #print(imgArray.shape, imgArray.dtype)
        #print("Got image")
        cv2.imshow("Drone View", self.displayImage)
        
    def testNextPicture(self):
        """Takes a picture from the drone, and converts it to display
        in tkinter.  It reschedules itself to run every second"""
        pass

    def nav2String(self, navData):
        st = """ """
        for k in navData:
            line = str(k) + ": " + str(navData[k]) + "\n"
            st += line
        return st

def runDrone():
    """This runs the drone program"""
    foo = ShowImages()
    foo.go()

runDrone()
