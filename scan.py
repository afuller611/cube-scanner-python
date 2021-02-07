# Python code for Cube Scanner


import numpy as np
from matplotlib import pyplot as plt
import cv2
import imutils
import math
from types import SimpleNamespace


# Capturing video through webcam
webcam = cv2.VideoCapture(0)

upper_left = (0, 245)
bottom_right = (765, 485)


def isContourSquare(c):
    # approximate the contour
    peri = cv2.arcLength(c, True)
    # the contour is 'bad' if it is not a rectangle
    area = cv2.contourArea(c)

    # Find the circularity of the contour, a square's should be about 0.785
    squareness = 4 * math.pi * area / math.pow(peri, 2)
    if (area > 500 and squareness >= 0.68 and squareness <= 0.9):
        return True
    else:
        return False
    


# Start a while loop 
while(1): 
      
    # webcam in image frames 
    _, imageFrame = webcam.read()
    scanFrame = imageFrame[upper_left[1] : bottom_right[1], upper_left[0] : bottom_right[0]]

    # Get what contours should be

    # Make a copy of the image frame to change it
    contourImage = imageFrame

    # Gray the image cause that helps for some reason
    gray = cv2.cvtColor(contourImage, cv2.COLOR_BGR2GRAY)

    # Give it a bit of a blur beacuse that also helps for some reason
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Canny does something to get edge detection, not sure what
    canny = cv2.Canny(blurred, 20, 40)

    # Kernel is for the dilation step
    kernel = np.ones((3, 3), np.uint8)

    # Dilating the lines to help detect edges better
    dilated = cv2.dilate(canny, kernel, iterations=2)

    #Finally find the contours
    (contours, hierarchy) = cv2.findContours(dilated.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


    colors = []
    squares = []
    for i in range(len(contours)):
    # Check to see if the contour is square, and that it doesn't have a child, or, if it does have a child, that the child is not square
    # See this article to understand hiearchy https://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html (for some reason hierarchy is as an array of length 1 - real data is nested in there)
        if (isContourSquare(contours[i]) and (hierarchy[0][i][2] == -1 or not isContourSquare(contours[hierarchy[0][i][2]]))):
            # If it's square, let's grab the "bounding rectangle" -- returns x, y, width and height
            x,y,w,h = cv2.boundingRect(contours[i])
            color = np.array(cv2.mean(imageFrame[y:y+h,x:x+w])).astype(np.uint8)

            square = SimpleNamespace(x=x, y=y, color=color)
            squares.append(square)
            # Then draw that rectangle on the image frame
            cv2.rectangle(imageFrame, (x,y), (x+w, y+h), (0, 255, 0), 3)

    # Might want to add some kind of logic so it checks that there are 8 squares and that they're about the same spot they were in previous frames. Can also check to see if colors stay the same in multiple frames.
    if (len(squares) > 8):

        # Sort the 9 squares found by y coordinate
        sortedByYSquares = sorted(squares, key=lambda square: square.y)

        # Separate into 3 rows (this is done before sorting by x because the y coordinate could be a little bit off from others in the row)
        topRow = sorted([sortedByYSquares[0], sortedByYSquares[1], sortedByYSquares[2]], key=lambda square: square.x)
        middleRow = sorted([sortedByYSquares[3], sortedByYSquares[4], sortedByYSquares[5]], key=lambda square: square.x)
        bottomRow = sorted([sortedByYSquares[6], sortedByYSquares[7], sortedByYSquares[8]], key=lambda square: square.x)

        # Combine the rows to make an array of 3 arrays
        faceNotFlattened = [topRow, middleRow, bottomRow]

        # Flatten that array into an array of 9 squares
        sortedFace = []
        for row in faceNotFlattened:
            for square in row:
                sortedFace.append(square)
        
        # Print that face
        print(sortedFace)

        # Take a screenshot of when the face was read for testing
        cv2.imwrite("test.png", imageFrame)
        cv2.destroyAllWindows() 
        break
    # cv2.drawContours(imageFrame, newContours, -1, (0, 255, 0), 3)

    # Program Termination 
    cv2.imshow("Cube Scanner", imageFrame) 

    if cv2.waitKey(10) & 0xFF == ord('q'): 
        cv2.destroyAllWindows() 
        break
