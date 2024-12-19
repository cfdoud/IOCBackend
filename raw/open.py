import cv2
import numpy as np

# Define the known reference RGB values of the X-Rite ColorChecker Classic patches
reference_colors = np.array([
    [115, 82, 68],  # Dark Skin
    [194, 150, 130],  # Light Skin
    [98, 122, 157],  # Blue Sky
    [87, 108, 67],  # Foliage
    [133, 128, 177],  # Blue Flower
    [103, 189, 170],  # Bluish Green
    [214, 126, 44],  # Orange
    [80, 91, 166],  # Purplish Blue
    [193, 90, 99],  # Moderate Red
    [94, 60, 108],  # Purple
    [157, 188, 64],  # Yellow Green
    [224, 163, 46],  # Orange Yellow
    [56, 61, 150],  # Blue
    [70, 148, 73],  # Green
    [175, 54, 60],  # Red
    [231, 199, 31],  # Yellow
    [187, 86, 149],  # Magenta
    [8, 133, 161],  # Cyan
    [243, 243, 242],  # White
    [200, 200, 200],  # Neutral 8
    [160, 160, 160],  # Neutral 6
    [122, 122, 121],  # Neutral 5
    [85, 85, 85],  # Neutral 3.5
    [52, 52, 52]  # Black
]) /255.0

# Load the image containing the ColorChecker Classic
image = cv2.imread(r'C:\Users\proud\Documents\Code\BackendIOC\raw\test2.jpg')  # Update this to your image path

# Convert to RGB for processing
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Define the coordinates of the ColorChecker patches (you need to adjust these based on your image)
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
# Corrected coordinates format (x_start, y_start, x_end, y_end)

detected_colors = []
for i, (x_start, y_start, x_end, y_end) in enumerate(patch_coordinates):
    patch = image_rgb[y_start:y_end, x_start:x_end]
    avg_color = np.mean(patch, axis=(0, 1)) / 255.0  # Normalize to 0-1 range
    detected_colors.append(avg_color)
detected_colors = np.array(detected_colors)

# Calculate the transformation matrix using least squares
transformation_matrix, _, _, _ = np.linalg.lstsq(detected_colors, reference_colors, rcond=None)

# Apply the transformation matrix
image_flattened = image_rgb.reshape((-1, 3)) / 255.0  # Normalize pixel values
corrected_image_flattened = np.dot(image_flattened, transformation_matrix.T)
corrected_image_flattened = np.clip(corrected_image_flattened, 0, 1) * 255
corrected_image_rgb = corrected_image_flattened.reshape(image_rgb.shape).astype(np.uint8)

# Apply subtle adjustments to each channel to balance the colors
red_scale = 2  # Slight adjustment to red channel
green_scale = 1.06  # No change to green
blue_scale = 0.95  # Slight increase to reduce blue

# Adjust each channel
corrected_image_rgb[:, :, 0] = np.clip(corrected_image_rgb[:, :, 0] * red_scale, 0, 255)  # Red channel
corrected_image_rgb[:, :, 1] = np.clip(corrected_image_rgb[:, :, 1] * green_scale, 0, 255)  # Green channel
corrected_image_rgb[:, :, 2] = np.clip(corrected_image_rgb[:, :, 2] * blue_scale, 0, 255)  # Blue channel

# Convert back to BGR for display
corrected_image_bgr = cv2.cvtColor(corrected_image_rgb, cv2.COLOR_RGB2BGR)

# Show original and corrected images
cv2.imshow('Original Image', image)
cv2.imshow('Corrected Image', corrected_image_bgr)
cv2.waitKey(0)
cv2.destroyAllWindows()