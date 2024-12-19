import cv2
import numpy as np
import tkinter as tk
from tkinter import Scale
from tkinter import Label

# Load the image
image_path = r'C:\Users\proud\Documents\Code\BackendIOC\raw\test2.jpg'  # Update with your image path
image = cv2.imread(image_path)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Function to apply live color correction
def apply_correction(red_scale, green_scale, blue_scale):
    # Apply scaling factors to the RGB channels
    corrected_image_rgb = image_rgb.copy().astype(np.float32)
    corrected_image_rgb[:, :, 0] *= red_scale  # Apply red scaling
    corrected_image_rgb[:, :, 1] *= green_scale  # Apply green scaling
    corrected_image_rgb[:, :, 2] *= blue_scale  # Apply blue scaling

    # Clip values to stay within valid RGB range (0-255)
    corrected_image_rgb = np.clip(corrected_image_rgb, 0, 255).astype(np.uint8)

    # Convert back to BGR for OpenCV display
    corrected_image_bgr = cv2.cvtColor(corrected_image_rgb, cv2.COLOR_RGB2BGR)

    # Display the corrected image
    cv2.imshow('Corrected Image', corrected_image_bgr)
    cv2.waitKey(1)  # Wait for a key press to update the image

# Create a Tkinter window
window = tk.Tk()
window.title('Live Color Correction')

# Create sliders for red, green, and blue scaling
red_scale_slider = Scale(window, from_=0.5, to=1.5, resolution=0.01, orient="horizontal", label="Red Scale")
green_scale_slider = Scale(window, from_=0.5, to=1.5, resolution=0.01, orient="horizontal", label="Green Scale")
blue_scale_slider = Scale(window, from_=0.5, to=1.5, resolution=0.01, orient="horizontal", label="Blue Scale")

# Set initial values for sliders
red_scale_slider.set(1.0)
green_scale_slider.set(1.0)
blue_scale_slider.set(1.0)

# Function to update the image with the current slider values
def update_image():
    red_scale = red_scale_slider.get()
    green_scale = green_scale_slider.get()
    blue_scale = blue_scale_slider.get()
    apply_correction(red_scale, green_scale, blue_scale)

# Add labels for sliders
Label(window, text="Adjust Color Correction").pack()

# Place sliders in the window
red_scale_slider.pack()
green_scale_slider.pack()
blue_scale_slider.pack()

# Add a button to trigger live update
update_button = tk.Button(window, text="Update Image", command=update_image)
update_button.pack()

# Start the Tkinter event loop
window.mainloop()

# Close the OpenCV windows when done
cv2.destroyAllWindows()
