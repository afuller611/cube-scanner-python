# Python code for Cube Scanner


import numpy as np
from matplotlib import pyplot as plt
import cv2
import math
import json
from sklearn.cluster import KMeans
from k_means_constrained import KMeansConstrained


def isContourSquare(c):

    peri = cv2.arcLength(c, True)
    area = cv2.contourArea(c)

    # Find the circularity of the contour, a square's should be about 0.785
    squareness = 4 * math.pi * area / math.pow(peri, 2)
    if (area > 500 and squareness >= 0.70 and squareness <= 0.85):
        return True
    else:
        return False


def scanSide(imageFrame, faceName):
    # Make a copy of the image frame to change it
    contourImage = imageFrame.copy()

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

    # Finally find the contours
    (contours, hierarchy) = cv2.findContours(
        dilated.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    squares = []

    for i in range(len(contours)):
        # Check to see if the contour is square, and that it doesn't have a child, or, if it does have a child, that the child is not square
        # See this article to understand hiearchy https://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html (for some reason hierarchy is as an array of length 1 - real data is nested in there)
        if (isContourSquare(contours[i]) and (hierarchy[0][i][2] == -1 or not isContourSquare(contours[hierarchy[0][i][2]]))):
            # If it's square, let's grab the "bounding rectangle" -- returns x, y, width and height
            x, y, w, h = cv2.boundingRect(contours[i])

            # Grab color
            avgColor = np.array(
                cv2.mean(contourImage[y+2:y+h-2, x+2:x+w-2])).astype(np.uint8)

            # Save square as object
            square = {
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "avgColor": avgColor.tolist()
            }

            # Append square to array of squares
            squares.append(square)

            # Then draw that rectangle on the image frame
            cv2.rectangle(imageFrame, (x, y), (x+w, y+h), (0, 255, 0), 3)

    # Might want to add some kind of logic so it checks that there are 8 squares
    # and that they're about the same spot they were in previous frames.
    #  Can also check to see if colors stay the same in multiple frames.
    if (len(squares) == 9):

        # Sort the 9 squares found by y coordinate
        sortedByYSquares = sorted(squares, key=lambda square: square["y"])

        # Separate into 3 rows (this is done before sorting by x because the y coordinate could be a little bit off from others in the row)
        topRow = sorted([sortedByYSquares[0], sortedByYSquares[1],
                         sortedByYSquares[2]], key=lambda square: square["x"])
        middleRow = sorted([sortedByYSquares[3], sortedByYSquares[4],
                            sortedByYSquares[5]], key=lambda square: square["x"])
        bottomRow = sorted([sortedByYSquares[6], sortedByYSquares[7],
                            sortedByYSquares[8]], key=lambda square: square["x"])

        # Combine the rows to make an array of 3 arrays
        faceNotFlattened = [topRow, middleRow, bottomRow]

        # Flatten that array into an array of 9 squares
        sortedFace = []
        for row in faceNotFlattened:
            for square in row:
                sortedFace.append(square)

        # Take a screenshot
        cv2.imwrite(faceName, imageFrame)

        # print(sortedFace)
        # Print that face
        return sortedFace
    else:
        return False


# Capturing video through webcam
webcam = cv2.VideoCapture(0)

upper_left = (0, 245)
bottom_right = (765, 485)

scanNow = True
scannedSides = []
scannedSidesWithLabels = {}

# Start a while loop
# while(1):

sideLabels = {
    0: "front",
    1: "left",
    2: "back",
    3: "right",
    4: "up",
    5: "down"
}

loops = 0

while(len(scannedSides) < 6):

    # webcam in image frames
    _, imageFrame = webcam.read()

    # While scanned sides is less than 7
    # Scan side
    scannedSide = False

    # This is kinda hacky...but not sure how to do a sleep without freezing the frame, supposed this won't matter for hololens though
    if (loops > 100):
        scanNow = True

    if (scanNow):
        scannedSide = scanSide(imageFrame, str(len(scannedSides)) + ".png")

    if (bool(scannedSide)):
        scannedSides.append(scannedSide)
        scanNow = False
        loops = 0

    cv2.imshow("Cube Scanner", imageFrame)

    if (not scanNow and loops == 0):
        if (len(scannedSides) == 1 or len(scannedSides) == 2 or len(scannedSides) == 3):
            print("Rotate Cube to the Left")
        if (len(scannedSides) == 4):
            print("Rotate Cube Up")
        if (len(scannedSides) == 5):
            print("Rotate Cube Up Twice")
    if len(scannedSides) > 5:
        for i in range(len(scannedSides)):
            scannedSidesWithLabels[sideLabels[i]] = scannedSides[i]

        # Map over scanned sides and get an array of all BGR values for each square
        allCubes = []
        for face in scannedSides:
            for square in face:
                allCubes.append(
                    [square["avgColor"][0], square["avgColor"][1], square["avgColor"][2]])

        # https://joshlk.github.io/k-means-constrained/
        # Calculate Kmeans and cluster colors with min/max size of 9
        kmeans = KMeansConstrained(n_clusters=6, size_min=9, size_max=9)
        k = kmeans.fit
        labels = kmeans.fit_predict(allCubes)

        # Object to hold all colors
        cube = {
            "front": [],
            "left": [],
            "back": [],
            "right": [],
            "up": [],
            "down": []
        }

        # Loop over the cluster data and get cube map based on cluster
        for i in range(len(labels)):
            if (i >= 0 and i <= 8):
                cube["front"].append(int(labels[i]))
            elif (i >= 9 and i <= 17):
                cube["left"].append(int(labels[i]))
            elif (i >= 18 and i <= 26):
                cube["back"].append(int(labels[i]))
            elif (i >= 27 and i <= 35):
                cube["right"].append(int(labels[i]))
            elif (i >= 36 and i <= 44):
                cube["up"].append(int(labels[i]))
            else:
                cube["down"].append(int(labels[i]))


        f = open("cubemap.txt", "w")
        json_str = json.dumps(cube)
        f.write(json_str)
        f.close()

        f = open("cubescandata.txt", "w")
        json_str = json.dumps(scannedSidesWithLabels)
        f.write(json_str)
        f.close()

    loops += 1
    # Program Termination
    if cv2.waitKey(10) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
