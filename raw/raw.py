from PIL import Image
import numpy as np 

# Open the TIFF image
img = Image.open(r'C:\Users\proud\Documents\Code\BackendIOC\raw\pc.tiff')
img.show()  # Display the image

# Convert the image to a numpy array for pixel manipulation
image_array = np.array(img)

# Display shape and a sample of pixel values
print(image_array.shape)  # This will give the dimensions of the image
print(image_array[0][0])  # This will print the pixel value of the top-left corner

# Example of extracting RGB values of a specific region (assuming the color checker is at a fixed position)
color_checker_region = image_array[100:200, 100:200]  # Slice out the region of interest
average_color = np.mean(color_checker_region, axis=(0, 1))  # Average color in the region
print(average_color)  # Print the RGB values


# Assume you have the known reference colors (reference_color) and the measured colors (measured_color)
reference_color = np.array([255, 255, 255])  # Example: the color of a white patch on the color checker
measured_color = np.mean(color_checker_region, axis=(0, 1))

# Calculate the color correction matrix
correction_matrix = reference_color / measured_color

# Apply the correction to the entire image
# Apply the correction and clip values to be between 0 and 255
corrected_image_array = np.clip(image_array * correction_matrix, 0, 255)
corrected_image = Image.fromarray(np.uint8(corrected_image_array))
corrected_image.show()


corrected_image.save('corrected_image.tiff')
