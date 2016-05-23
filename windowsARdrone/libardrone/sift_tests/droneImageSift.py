# -*- coding: utf-8 -*-
"""
Created on Mon May 09 14:02:30 2016

@author: mju
"""

import numpy as np
import cv2
import os
from operator import itemgetter
#from matplotlib import pyplot as plt


def drawMatches(img1, kp1, img2, kp2, matches):
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

    out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')

    # Place the first image to the left
    out[:rows1,:cols1] = np.dstack([img1, img1, img1])

    # Place the next image to the right of it
    out[:rows2,cols1:] = np.dstack([img2, img2, img2])

    # For each pair of points we have between both images
    # draw circles, then connect a line between them
    for mat in matches:

        # Get the matching keypoints for each of the images
        img1_idx = mat[0].queryIdx
        img2_idx = mat[0].trainIdx

        # x - columns
        # y - rows
        (x1,y1) = kp1[img1_idx].pt
        (x2,y2) = kp2[img2_idx].pt

        # Draw a small circle at both co-ordinates
        # radius 4
        # colour blue
        # thickness = 1
        cv2.circle(out, (int(x1),int(y1)), 4, (255, 0, 0), 1)   
        cv2.circle(out, (int(x2)+cols1,int(y2)), 4, (255, 0, 0), 1)

        # Draw a line in between the two points
        # thickness = 1
        # colour blue
        cv2.line(out, (int(x1),int(y1)), (int(x2)+cols1,int(y2)), (255, 0, 0), 1)


    # Show the image
    cv2.imshow('Matched Features', out)
    cv2.waitKey(0)
    cv2.destroyWindow('Matched Features')

def tryToMatchFeatures(sift, img1, pointInfo):
    #cv2.imshow("source", img1)
    #cv2.imshow("check", img2)
    #cv2.waitKey(0)

    kp2, des2 = pointInfo

    # Initiate SIFT detector
    sift = cv2.SIFT()
    
#    if img1 is None or img2 is None:
#        print("it thinks the images are none")
#        return [], None, None

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    #kp2, des2 = sift.detectAndCompute(img2,None)

    if des1 is None or des2 is None:
        #print("it thinks the key descriptions are none")
        #print("des one", des1, "des two", des2)
        #print("kp one", kp1, "kp two", kp2)
        return [], None, None
    elif len(des1) == 0 or len(des2) == 0:
        print("it thinks the key descriptions are empty")
        return [], None, None
        
        
    #print("1: ", des1, "len: ", len(des1), "2: ", des2, "len: ", len(des2))

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
    #properties[i][2] holds the list of good points and the two sets of keypoints (for drawing)
    #print("This is in find image:", properties[i][1])
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
    print(scores)
    max_index, max_value = max(enumerate(scores), key=itemgetter(1))
    
    if max_value > 20:
        print('Run ' + str(j) + ': The '+ str(itemsSought[max_index]) + ' sign was detected, with ' + str(max_value) + ' points')
        drawMatches(img, properties[i][2][1], properties[max_index][0], properties[i][2][2], properties[i][2][0])
    else:
        print('No sign was detected')
        
    #cleanup
    for i in range (0, len(itemsSought)):
        properties[i][2] = []
        properties[i][3] = 0

itemsSought = ['hatch', 'exit']
properties = [] #2D array used to store info on each item: item i is properties[i]

sift = cv2.SIFT()

#properties[i][0] holds the reference image for the item
for i in range (0, len(itemsSought)):
    properties.append([None, [], [], 0])
    
    filename = itemsSought[i] + 'Ref.jpg'
    path = os.path.join("dronecaps", filename)
    properties[i][0] = cv2.imread(path, 0)
    if properties[i][0] is None:
        print("Reference image", itemsSought[i], "not found")
    #cv2.imshow("reference:", properties[i][0])
    #properties[i][1] holds the keypoints and their descriptions for the reference image
    keypoints, descriptions = sift.detectAndCompute(properties[i][0], None)
    properties[i][1].append(keypoints)
    properties[i][1].append(descriptions)
    
for j in range (1, 39): #hard-coded for number of images you're checking
    #print('cap' + str(i) +'.jpg')
    filename = 'cap' + str(j) + '.jpg'
    path = os.path.join("dronecaps", filename)
    img = cv2.imread(path, 0)
    if img is None:
        print("Target image", filename, "not found")
    findImage(img, properties, itemsSought, j)


#    door = cv2.imread(os.path.join("dronecaps", "doorRef.jpg"),0) # trainImage
#    hatch = cv2.imread(os.path.join("dronecaps", "hatchRef.jpg"),0) # trainImage
#    ex = cv2.imread(os.path.join("dronecaps", "exitRef.jpg"),0) # trainImage
    
#    doorKeys, doorDes = sift.detectAndCompute(door, None)
#    hatchKeys, hatchDes  = sift.detectAndCompute(hatch, None)
#    exKeys, exDes  = sift.detectAndCompute(ex, None)

#    doorPoints, doorKeys1, doorKeys2 = tryToMatchFeatures(sift, img, doorKeys, doorDes)
#    hatchPoints, hatchKeys1, hatchKeys2  = tryToMatchFeatures(sift, img, hatchKeys, hatchDes)
#    exPoints, exKeys1, exKeys2  = tryToMatchFeatures(sift, img, exKeys, exDes)

#    if doorLen > hatchLen and doorLen > exLen and doorLen > 15:
#        print("Run", i, ": The door sign was detected: ", len(doorPoints), "points ")
#        img3 = drawMatches(img, doorKeys1, door, doorKeys2, doorPoints)
#    elif exLen > hatchLen and exLen > 15:
#        print("Run", i, ": The exit sign was detected: ", len(exPoints), "points ")
#        img3 = drawMatches(img, exKeys1, ex, exKeys2, exPoints)
#    elif hatchLen > 15:
#        print("Run", i, ": The hatch sign was detected: ", len(hatchPoints), "points ")
#        img3 = drawMatches(img, hatchKeys1, hatch, hatchKeys2, hatchPoints)
#    else:
#        print("There was no sign found.")
        #return None


#    #path = ".." + os.path.join(os.sep, "res", "images", "patternBar.jpg")
#    path = os.path.join("dronecaps", "exitRef.jpg")
#    pattern = cv2.imread(path,0) # trainImage
#    sift = cv2.SIFT()
#    kp, des = sift.detectAndCompute(pattern,None)
#    
#    #print("kp", kp, "des", des)
#    
#    points, kp1, kp2 = tryToMatchFeatures(img, kp, des)
#    
#    if len(points) > 25:
#        print("Run", i, ": The pattern was detected: ", len(points), "points ")
#        img3 = drawMatches(img,kp1,pattern,kp2,points)
#    else:
#        print("There was no sign found.")
        
    
#    doorLen = len(doorPoints)
#    hatchLen = len(hatchPoints)
#    exLen = len(exPoints)
    