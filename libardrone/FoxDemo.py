import Tkinter
from PIL import Image as PILImage, ImageTk
import libardrone
import time
from MultiCamShift import *


class ShowImages:
    def __init__(self):
        self.drone = None
        self.main = Tkinter.Tk()
        self.picLabel = Tkinter.Label(self.main, text = "Waiting for ARDrone image")
        self.picLabel.grid(row = 0, column = 0)
        
        self.dataLabel = Tkinter.Label(self.main, text = "Waiting for Navdata")
        self.dataLabel.grid(row=1, column = 0)
        
        self.main.bind_all('<Any-KeyPress>', self.respondToKeyPress)
        #self.main.bind('<KeyPress-n>', self.nextPicture)
        #self.main.bind('<KeyPress-r>', self.resetDrone)
        #self.main.bind('<KeyPress-Return>', self.takeoff)
        #self.main.bind('<KeyPress- >', self.land)
        #self.main.bind('<KeyPress-Up>', self.moveUp)
        #self.main.bind('<KeyPress-Down>', self.moveDown)
        #self.main.bind('<KeyPress-Left>', self.turnLeft)
        #self.main.bind('<KeyPress-Right>', self.turnRight)
        #self.main.bind('<KeyPress-w>', self.moveForward)
        #self.main.bind('<KeyPress-s>', self.moveBackward)
        #self.main.bind('<KeyPress-a>', self.bankLeft)
        #self.main.bind('<KeyPress-d>', self.bankRight)
        self.main.bind_all('<Any-KeyRelease>', self.keyRelease)
        self.drone = libardrone.ARDrone(True)
        
        self.mcs = MultiCamShift(self.drone, self)
        self.mcs.start()
        
    def keyRelease(self, event):
        if event.char.lower() == 'q':
            self.quit()
        else:
            self.drone.hover()
            self.nextPicture()
            print("Key released:", event.keysym)
        
    def respondToKeyPress(self, event):
        respondText = 'Key press ' + event.keysym + ': '
        key = event.char.lower()
        if key == 'n':
            self.nextPicture()
            respondText += "Taking picture"
        elif key == 'r':
            self.drone.land()
            self.drone.reset()
            respondText += "Resetting drone"
        elif event.keysym == 'Return':
            self.drone.takeoff()
            respondText += "Taking off"
        elif key == ' ':
            self.drone.land()
            respondText += "Landing"
        elif event.keysym == 'Up':
            self.drone.move_up()
            respondText += "Moving up"
        elif event.keysym == 'Down':
            self.drone.move_down()
            respondText += "Moving down"
        elif event.keysym == 'Left':
            self.drone.turn_left()
            respondText += "Turning left"
        elif event.keysym == 'Right':
            self.drone.turn_right()
            respondText += 'Turning right'
        elif key == 'w':
            self.drone.move_forward()
            respondText += 'Moving forward'
        elif key == 's':
            self.drone.move_backward()
            respondText += 'Moving backward'
        elif key == 'a':
            self.drone.move_left()
            respondText += 'Moving left'
        elif key == 'd':
            self.drone.move_right()
            respondText += 'Moving right'
        elif key != '' and key in '1234567890':
            newSpeed = self.keyToSpeed(event.char)
            self.drone.speed = newSpeed
            respondText += 'Changing speed to ' + str(newSpeed)
        self.outputResponse(respondText)


    def keyToSpeed(self, key):
        if key == '0':
            return 1.0
        else:
            num = int(key)
            return num / 10.0
        
    def outputResponse(self, text):
        self.dataLabel['text'] = text
        print(text)

 
    def nextPicture(self):
        imgArray = self.drone.image
        navData = self.drone.navdata
        pilPic = PILImage.fromarray(imgArray)
        #if event != 'foo':
            #pilPic.show()
        self.currPic = ImageTk.PhotoImage(pilPic)
        self.picLabel['image'] = self.currPic
        
        #navStr = str(navData)
        #self.dataLabel['text'] = navStr
        
        
    def quit(self):
        self.drone.land()
        print("Quitting!")
        time.sleep(2)
        self.mcs.stop()
        self.main.destroy()
        
    def go(self):
        self.main.mainloop()
    
    

def runDrone():
    foo = ShowImages()
    foo.go()
    
runDrone()