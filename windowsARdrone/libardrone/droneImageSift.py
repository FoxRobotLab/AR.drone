# -*- coding: utf-8 -*-
"""
Created on Mon May 09 14:02:30 2016

@author: mju
"""

import numpy as np
#import math
import os
from operator import itemgetter
import sys
#from matplotlib import pyplot as plt

sys.path.append("C:/Anaconda/Lib/site-packages")

import cv2


def drawMatches(img1, kp1, img2, kp2, matches, colorImage):
    """
     Code based on a stackoverflow post.
     see http://stackoverflow.com/questions/20259025/module-object-has-no-attribute-drawmatches-opencv-python
    
    img1,img2 - Grayscale images
    kp1,kp2 - Detected list of keypoints through any of the OpenCV keypoint 
              detection algorithms
    matches - A list of matches of corresponding keypoints through any
              OpenCV keypoint matching algorithm
    """

    rows1 = img1.shape[0]
    cols1 = img1.shape[1]

    black = np.zeros((rows1, cols1), dtype='uint8')
    
    # For each pair of points we have between both images
    for mat in matches:

        # Get the matching keypoints for each of the images
        img1_idx = mat[0].queryIdx
        img2_idx = mat[0].trainIdx

        # x - columns
        # y - rows
        (x1,y1) = kp1[img1_idx].pt
        (x2,y2) = kp2[img2_idx].pt
        
        #draw large-ish white circles around each of the keypoints
        cv2.circle(black, (int(x1),int(y1)), 10, (255, 255, 255), -1)  
        
    #use closing to eliminate the white spots not in "clusters" - the noise keypoints
    kernel = np.ones((15,15),np.uint8)
    closing = cv2.morphologyEx(black, cv2.MORPH_CLOSE, kernel)
    
    #find contour of the remaining white blob. There may be small noise blobs, but we're
    #pretty sure that the largest is the one we want.
    _, contours, hierarchy = cv2.findContours(closing, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cv2.contourArea(contours[0])

    maxArea = 0
    largestContour = 0

    for i in range (0, len(contours)):
        contour = contours[i]
        area = cv2.contourArea(contour) 
        if area > maxArea:
            maxArea = area
            largestContour = contour
    
    #get the bounding rectangle (not rotated, because camshift Does Not Like That) of the
    #large blob we found.
    rect = cv2.boundingRect(largestContour)

    return rect

def tryToMatchFeatures(sift, img1, pointInfo):
    kp2, des2 = pointInfo

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)

    if des1 is None or des2 is None:
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
    
    #properties[i][2] holds the list of good points and the two sets of keypoints (for drawing)
    sift = cv2.xfeatures2d.SIFT_create()
    for i in range (0, len(itemsSought)):
        goodPoints, targetKeypts, refKeypts = tryToMatchFeatures(sift, img, properties[i][1])
        properties[i][2].append(goodPoints)
        properties[i][2].append(targetKeypts)
        properties[i][2].append(refKeypts)
    
        #properties[i][3] holds the len(goodPoints) - the number of good points of that item
        numGoodPoints = len(properties[i][2][0])
        properties[i][3] = numGoodPoints

    getcount = itemgetter(3)
    scores = map(getcount, properties)
    #print(scores)
    max_index, max_value = max(enumerate(scores), key=itemgetter(1))
    
    if max_value > 20:
        #print('Run ' + str(j) + ': The '+ str(itemsSought[max_index]) + ' sign was detected, with ' + str(max_value) + ' points')
        box = drawMatches(img, properties[max_index][2][1], properties[max_index][0], properties[max_index][2][2], properties[max_index][2][0], colorImage)
    else:
        #print('No sign was detected')
        return None
        
    #cleanup
    for i in range (0, len(itemsSought)):
        properties[i][2] = []
        properties[i][3] = 0
        
    return box
        
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

        #properties[i][1] holds the keypoints and their descriptions for the reference image
        keypoints, descriptions = sift.detectAndCompute(properties[i][0], None)
        properties[i][1].append(keypoints)
        properties[i][1].append(descriptions)
        
    return properties
    
#run this if you wanna test the feature recognition using still images in the dronecaps file
def scanImages():
    #add 'door' if you want but it's more inaccurate than the others, you're likely to get false positives
    itemsSought = ['hatch', 'exit']
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