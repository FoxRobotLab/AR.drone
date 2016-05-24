import numpy as np
import cv2
import math
from droneImageSift import *
from operator import itemgetter

frame = None
selection = None
track_window = None
hist = None


def showDiff(img1, img2):
    global selection
    global track_window
    global hist
    
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(gray1, gray2)

    #cv2.imshow("Difference", diff)
    solidColor = np.zeros((300, 300, 3), np.uint8)
    solidColor[:] = (225, 225, 225)

    #example code from boundingRect tutorial
    ret,thresh = cv2.threshold(diff,100,255,0)
    contours = cv2.findContours(thresh, 1, 2)
    cont0 = contours[0]

    x,y,w,h = cv2.boundingRect(cont0)
    cv2.rectangle(img2,(x,y),(x+w,y+h),(0,255,0),2)
    #cv2.imshow("Movement", img2)

    selection = (x, y, w, h)
    track_window = (x, y, w-x, h-y)

    hsv_roi = hsv[y:h, x:w]             # access the currently selected region and make a histogram of its hue 
    mask_roi = mask[y:h, x:w]
    hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    hist = hist.reshape(-1)

def turnPointsToRect(points):
    getcount = itemgetter(0)
    xcoords = map(getcount, points)
    getcount = itemgetter(1)
    ycoords = map(getcount, points)
    
    if xcoords[0] == xcoords[1] or xcoords[0] == xcoords[2]: #the rect is not tilted
        print("NO TILT")
        width = max(abs(xcoords[0] - xcoords[1]), abs(xcoords[0] - xcoords[2]))
        height = max(abs(ycoords[0] - ycoords[1]), abs(ycoords[0] - ycoords[2]))
        cx = int(math.floor(min(xcoords) + (width/2)))
        cy = int(math.floor(min(ycoords) + (height/2)))
        
    else: #rectangle is tilted
        print("tiiiiiilllllllllllllt")
        max_x_index, max_x_value = max(enumerate(xcoords), key=itemgetter(0))
        min_x_index, min_x_value = min(enumerate(xcoords), key=itemgetter(0))
        max_y_index, max_y_value = max(enumerate(ycoords), key=itemgetter(1))
        min_y_index, min_y_value = min(enumerate(ycoords), key=itemgetter(1))
        
        cx = int(math.floor((max_x_value + min_x_value)/2))
        cy = int(math.floor((max_y_value + min_y_value)/2))
        
        #THIS IS NOT RIGHT - I'm not sure how width and height are differentiated, so I'm just not bothering
        #to be fixed when it becomes apparent which is which
        """The idea is as follows: make two right triangles with the hypontenuses as the two bottom edges
        of the rectangle. The lowest point on the rectangle (min_y) is in both of them. Then use the two other
        points - the ones that aren't the points with the lowest or highest y index - to determine by the
        Pythagorean theorem what the width and the height are."""
        #To fix, you just need some logic to determine which is height and which is width!
        indices = [0, 1, 2, 3]
        indices.remove(min_y_index)
        indices.remove(max_y_index)
        
        x0 = xcoords[ min_y_index]
        y0 = min_y_value
        x1 = xcoords[indices[0]]
        y1 = ycoords[indices[0]]
        x2 = xcoords[indices[1]]
        y2 = ycoords[indices[1]]
        
        width = int(math.floor(math.sqrt((x0 - x1)**2 + (y0 - y1)**2)))
        height = int(math.floor(math.sqrt((x0 - x2)**2 + (y0 - y2)**2)))
        
    return (cx, cy, width, height)    
    
def getNextFrame(vidObj):
    """Takes in the VideoCapture object and reads the next frame, returning one that is half the size 
    (Comment out that line if you want fullsize)."""
    ret, frame = vidObj.read()
    #print type(vidObj), type(frame)
    if frame is not None:
        frame = cv2.resize(frame, (0, 0), fx = 0.5, fy = 0.5)
    return frame

cam = cv2.VideoCapture(0)
ret, frame = cam.read()
#print type(frame)
cv2.namedWindow('camshift')

rect = None

# start processing frames
while True:
    frame1 = getNextFrame(cam)
    frame2 = getNextFrame(cam)

    #from camShiftDemo
    hsv = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)    # convert to HSV
    mask = cv2.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))   # eliminate low and high saturation and value values

    vis1 = frame1.copy()
    vis2 = frame2.copy()

    if track_window is None: # or track_window[0] < 1 or track_window[1] < 1 or track_window[2] < 1 or track_window[3] < 1
        #showDiff(vis1, vis2) 
        itemsSought = ['hatch', 'exit']
        properties = initRefs(itemsSought)
        rect = findImage(vis1, properties, itemsSought, 0)
        if rect is not None: #if findImage didn't return anything, just pass and try again
            #print(rect)
            #box = cv2.boxPoints(rect)
            #box = np.int0(box)
            #for i in range (0, 4):
            #    cv2.line(vis2, tuple(box[i]), tuple(box[(i+1)%4]), (255, 0, 0))
            #box_points = turnPointsToRect(result)
            #x,y,w,h = box_points
            #selection = (x,y,w,h)
            #track_window = (x, y, w, h)
            #track_window = rect
            #print("track_window ", track_window)
            
            
            x, y, w, h = rect
            cv2.rectangle(vis2,(x,y),(x+w,y+h),(0,255,0),2)
#            x, y = rect[0]
#            w, h = rect[1]
#            x = int(math.floor(x))
#            y = int(math.floor(y))
#            w = int(math.floor(w))
#            h = int(math.floor(h))
            #track_window = (x, y, w+x, h+y)
            track_window = (x, y, w, h)
                
            hsv_roi = hsv[y:h, x:w]             # access the currently selected region and make a histogram of its hue 
            mask_roi = mask[y:h, x:w]
            hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
            cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
            hist = hist.reshape(-1)
        
    else: #from camShiftDemo
        print("WELLL")
        #selection = None
        #selection = ()
        #print("track window was ", track_window)
        prob = cv2.calcBackProject([hsv], [0], hist, [0, 180], 1)
        prob &= mask
        term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
        #print(track_window)
        track_box, track_window = cv2.CamShift(prob, track_window, term_crit)
        #print("track window is ", track_window)
        try:
            #print("ellipse printed fine")
            cv2.ellipse(vis2, track_box, (0, 0, 255), 2)
            #cv2.imshow('vis2', vis2)
        except:
            print("YIKES that didn't work - couldn't print the ellipse")
            print track_box
        
    #print("it was fine and now we're here")
    cv2.imshow('camshift', vis2)

    ch = 0xFF & cv2.waitKey(5)
    if ch == 27:
        break

        
cv2.destroyAllWindows()


