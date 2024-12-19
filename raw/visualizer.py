import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image
image = cv2.imread(r'C:\Users\proud\Documents\Code\BackendIOC\raw\test2.jpg')  # Update this to your image path
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Define the patch coordinates
patch_coordinates = [
    (355, 105, 548, 288), 
    (592, 95, 793, 290), 
    (830, 97, 1031, 287), 
    (1072, 100, 1268, 287), 
    (1309, 99, 1505, 289), 
    (1542, 103, 1728, 289), 
    (342, 333, 542, 526), 
    (591, 333, 790, 524), 
    (834, 331, 1032, 523), 
    (1074, 335, 1270, 518), 
    (1314, 333, 1509, 521), 
    (1549, 334, 1736, 520), 
    (336, 574, 538, 767), 
    (584, 572, 788, 768), 
    (833, 572, 1034, 763), 
    (1075, 571, 1280, 762), 
    (1317, 570, 1513, 753), 
    (1548, 571, 1743, 745), 
    (325, 823, 526, 1021), 
    (582, 821, 784, 1020), 
    (835, 817, 1035, 1013), 
    (1081, 815, 1279, 1005), 
    (1325, 813, 1517, 996), 
    (1559, 824, 1740, 993)
]

# Initialize a list to store extracted patches
detected_colors = []

# Extract each patch
for (x1, y1, x2, y2) in patch_coordinates:
    patch = image_rgb[y1:y2, x1:x2]
    patches.append(patch)

# Create a figure to display the patches
num_patches = len(patches)
cols = 6  # Number of patches per row
rows = (num_patches + cols - 1) // cols  # Compute the number of rows required

plt.figure(figsize=(15, 5))
for i, patch in enumerate(patches):
    plt.subplot(rows, cols, i + 1)
    plt.imshow(patch)
    plt.axis('off')  # Turn off axis labels

plt.suptitle('Extracted Patches')
plt.tight_layout()
plt.show()
