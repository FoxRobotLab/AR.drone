# -*- coding: utf-8 -*-
"""
Created on Mon May 09 14:02:30 2016

@author: mju
"""

import numpy as np
import math
import os
from operator import itemgetter
import sys
#from matplotlib import pyplot as plt

sys.path.append("C:/Anaconda/Lib/site-packages")

import cv2


def drawMatches(img1, kp1, img2, kp2, matches, colorImage):
    """
     CODE FROM A LOVELY PERSON ON STACK OVERFLOW:
     see http://stackoverflow.com/questions/20259025/module-object-has-no-attribute-drawmatches-opencv-python
     I didn't have cv2.drawMatches in my version of opencv, so this was very useful.
    
    My own implementation of cv2.drawMatches as OpenCV 2.4.9
    does not have this function available but it's supported in
    OpenCV 3.0.0

    This function takes in two images with their associated 
    keypoints, as well as a list of DMatch data structure (matches) 
    that contains which keypoints matched in which images.

    An image will be produced where a montage is shown with
    the first image followed by the second image beside it.

    Keypoints are delineated with circles, while lines are connected
    between matching keypoints.

    img1,img2 - Grayscale images
    kp1,kp2 - Detected list of keypoints through any of the OpenCV keypoint 
              detection algorithms
    matches - A list of matches of corresponding keypoints through any
              OpenCV keypoint matching algorithm
    """

    # Create a new output image that concatenates the two images together
    # (a.k.a) a montage
    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]

    #out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')
    black = np.zeros((rows1, cols1), dtype='uint8')

    # Place the first image to the left
    #out[:rows1,:cols1] = np.dstack([img1, img1, img1])

    # Place the next image to the right of it
    #out[:rows2,cols1:] = np.dstack([img2, img2, img2])

    # For each pair of points we have between both images
    # draw circles, then connect a line between them
    #print(len(matches))
    for mat in matches:

        # Get the matching keypoints for each of the images
        img1_idx = mat[0].queryIdx
        img2_idx = mat[0].trainIdx

        # x - columns
        # y - rows
        (x1,y1) = kp1[img1_idx].pt
        #print("The whole point", x1, y1)
        (x2,y2) = kp2[img2_idx].pt

        # Draw a small circle at both co-ordinates
        # radius 4
        # colour blue
        # thickness = 1
        #cv2.circle(out, (int(x1),int(y1)), 4, (255, 0, 0), 1)   
        #cv2.circle(out, (int(x2)+cols1,int(y2)), 4, (255, 0, 0), 1)
        
        cv2.circle(black, (int(x1),int(y1)), 10, (255, 255, 255), -1)  

        # Draw a line in between the two points
        # thickness = 1
        # colour blue
        #cv2.line(out, (int(x1),int(y1)), (int(x2)+cols1,int(y2)), (255, 0, 0), 1)
        
    kernel = np.ones((15,15),np.uint8)
    #dilation = cv2.dilate(black, kernel, iterations = 1)
    closing = cv2.morphologyEx(black, cv2.MORPH_CLOSE, kernel)
    
    #contours, hierarchy, _ = cv2.findContours(closing, mode = cv2.RETR_LIST, method = cv2.CHAIN_APPROX_SIMPLE)
    _, contours, hierarchy = cv2.findContours(closing, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cv2.contourArea(contours[0])

    maxArea = 0
    largestContour = 0
    index = 0
#    for contour in contours:
#        area = cv2.contourArea(contour)
#        print(area)
#        if area > maxArea:
#            maxArea = area
#            largestContour = contour

    for i in range (0, len(contours)):
        contour = contours[i]
        area = cv2.contourArea(contour) 
        if area > maxArea:
            maxArea = area
            largestContour = contour
            index = i
            print("INDEX", index)
    #boundRect = cv2.boundingRect(largestContour)
    
            
    rect = cv2.minAreaRect(largestContour)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    print(box)
    cv2.drawContours(closing,contours,index,(255,255,255),2)
         
    #cv2.drawContours(closing,contours,index,(225,0,0))
    #cv2.rect(closing, box)
    for i in range (0, 4):
        cv2.line(colorImage, tuple(box[i]), tuple(box[(i+1)%4]), (255, 0, 0))

    # Show the image
    #cv2.imshow('Matched Features', out)
    #cv2.imshow('Oooh keypoints', closing)
    cv2.imshow('Feature found', colorImage)
    cv2.waitKey(0)
    #cv2.destroyWindow('Matched Features')
    #cv2.destroyWindow('Oooh keypoints')
    cv2.destroyWindow('Feature found')
    
def turnPointsToRect(points):
    getcount = itemgetter(0)
    xcoords = map(getcount, points)
    getcount = itemgetter(1)
    ycoords = map(getcount, points)
    
    if xcoords[0] == xcoords[1] or xcoords[0] == xcoords[2]: #the rect is not tilted
        width = max(abs(xcoords[0] - xcoords[1]), abs(xcoords[0] - xcoords[2]))
        height = max(abs(ycoords[0] - ycoords[1]), abs(ycoords[0] - ycoords[2]))
        cx = int(math.floor(min(xcoords) + (width/2)))
        cy = int(math.floor(min(ycoords) + (height/2)))
        
    else: #rectangle is tilted
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
        indices = (0, 1, 2, 3)
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

def tryToMatchFeatures(sift, img1, pointInfo):
    kp2, des2 = pointInfo

    # Initiate SIFT detector
    #sift = cv2.xfeatures2d.SIFT_create()

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)

    if des1 is None or des2 is None:
        #print("it thinks the key descriptions are none")
        #print("des one", des1, "des two", des2)
        #print("kp one", kp1, "kp two", kp2)
        return [], None, None
    elif len(des1) == 0 or len(des2) == 0:
        print("it thinks the key descriptions are empty")
        return [], None, None

    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1,des2, k=2)

    # Apply ratio test
    good = []
    for m,n in matches:
        if m.distance < 0.75*n.distance:
            good.append([m])
    
    return good, kp1, kp2

    
def findImage(img, properties, itemsSought, j):
    
    colorImage = img    
    #cv2.imshow("First", colorImage)
    #cv2.waitKey(0)
    
    #properties[i][2] holds the list of good points and the two sets of keypoints (for drawing)
    sift = cv2.xfeatures2d.SIFT_create()
    for i in range (0, len(itemsSought)):
        goodPoints, targetKeypts, refKeypts = tryToMatchFeatures(sift, img, properties[i][1])
        #cv2.imshow("next", colorImage)
        #cv2.waitKey(0)
        properties[i][2].append(goodPoints)
        properties[i][2].append(targetKeypts)
        properties[i][2].append(refKeypts)
    
        #properties[i][3] holds the len(goodPoints) - the number of good points of that item
        numGoodPoints = len(properties[i][2][0])
        properties[i][3] = numGoodPoints

    getcount = itemgetter(3)
    scores = map(getcount, properties)
    print(scores)
    max_index, max_value = max(enumerate(scores), key=itemgetter(1))
    
#    for k in range(0, max_value):
#        goodPoints = properties[max_index][2][0]
#        (x1,y1) = goodPoints[k].pt
#        print(x1, y1)
    
    if max_value > 20:
        print('Run ' + str(j) + ': The '+ str(itemsSought[max_index]) + ' sign was detected, with ' + str(max_value) + ' points')
        drawMatches(img, properties[max_index][2][1], properties[max_index][0], properties[max_index][2][2], properties[max_index][2][0], colorImage)
        #print('The good points were', properties[max_index][2][0])
    else:
        print('No sign was detected')
        
    #cleanup
    for i in range (0, len(itemsSought)):
        properties[i][2] = []
        properties[i][3] = 0
        
def initRefs(itemsSought):
    properties = [] #2D array used to store info on each item: item i is properties[i]
    
    sift = cv2.xfeatures2d.SIFT_create()
    
    #properties[i][0] holds the reference image for the item
    for i in range (0, len(itemsSought)):
        properties.append([None, [], [], 0])
        
        filename = itemsSought[i] + 'Ref.jpg'
        path = os.path.join("dronecaps", filename)
        properties[i][0] = cv2.imread(path, 0)
        if properties[i][0] is None:
            print("Reference image", itemsSought[i], "not found")
        
        #cv2.imshow("Please?", properties[i][0])
        #cv2.waitKey(0)
    
        #properties[i][1] holds the keypoints and their descriptions for the reference image
        keypoints, descriptions = sift.detectAndCompute(properties[i][0], None)
        properties[i][1].append(keypoints)
        properties[i][1].append(descriptions)
        
    return properties
    
itemsSought = ['hatch', 'exit'] #'door' if you want but it's pretty inaccurate
properties = initRefs(itemsSought)

for j in range (1, 39): #hard-coded for number of images you're checking
    filename = 'cap' + str(j) + '.jpg'
    path = os.path.join("dronecaps", filename)
    img = cv2.imread(path, 0)
    if img is None:
        print("Target image", filename, "not found")
    cv2.imshow("Come ON", img)
    cv2.waitKey(0)
    findImage(img, properties, itemsSought, j)