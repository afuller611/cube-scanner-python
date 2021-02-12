
import time

scanned_sides = 0
# While scanned sides is less than 7
while(scanned_sides < 7):
    # Scan side
    # Take screenshot of scanned image
    if (scanned_sides == 1 or scanned_sides == 2 or scanned_sides == 3):
        print("Rotate Cube to the Left")
        time.sleep(5)
    if (scanned_sides == 4):
        print("Rotate Cube Up")
        time.sleep(5)
    if (scanned_sides == 5):
        print("Rotate Cube Up Twice")
        time.sleep(5)

    scanned_sides += 1



# if scanned sides length < 4
# Next side text is "Rotate to left"
# if scanned sides == 4
# Next side text is "Rotate up"
# if scanned sides == 5
# Next side text is "Rotate twice up"

# Wait 5 seconds before starting loop again



















