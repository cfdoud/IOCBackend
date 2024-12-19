import cv2
import json

# Variables to store points and patches
drawing = False
ix, iy = -1, -1
patch_coordinates = []

# Mouse callback function
def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, patch_coordinates, img_copy
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Start drawing
        drawing = True
        ix, iy = x, y
    
    elif event == cv2.EVENT_MOUSEMOVE:
        # Visual feedback while dragging
        if drawing:
            img_temp = img_copy.copy()
            cv2.rectangle(img_temp, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('Image', img_temp)
    
    elif event == cv2.EVENT_LBUTTONUP:
        # Stop drawing and save the rectangle
        drawing = False
        patch_coordinates.append((ix, iy, x, y))
        cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.imshow('Image', img_copy)

# Load the image
img = cv2.imread(r'C:\Users\proud\Documents\Code\BackendIOC\raw\test2.jpg')  # Replace with your image path
img_copy = img.copy()

cv2.imshow('Image', img)
cv2.setMouseCallback('Image', draw_rectangle)

# Wait until 's' is pressed to save the coordinates or 'q' to quit
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):  # Save the coordinates
        with open('patch_coordinates.json', 'w') as f:
            json.dump(patch_coordinates, f)
        print("Patch coordinates saved:", patch_coordinates)
        break
    elif key == ord('q'):  # Quit without saving
        break

cv2.destroyAllWindows()
