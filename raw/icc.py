from PIL import ImageCms, Image

# Define file paths
input_image_path = r"C:\Users\proud\Documents\data\212\Screenshot 2025-02-12 195151.png"
icc_profile_path = r"C:\Windows\System32\spool\drivers\color\CameraProfile_New.icm"  # Your ICC profile
srgb_profile_path = r"C:\Windows\System32\spool\drivers\color\sRGB Color Space Profile.icm"  # sRGB profile
output_image_path = r"C:\Users\proud\Documents\data\212\THISISIT3.jpg"  # Output image

# Open the image
image = Image.open(input_image_path)

# Ensure it's in RGB mode (remove alpha if needed)
if image.mode == "RGBA":
    image = image.convert("RGB")

# Load ICC profiles
icc_profile = ImageCms.getOpenProfile(icc_profile_path)
srgb_profile = ImageCms.getOpenProfile(srgb_profile_path)

# Convert image from the camera profile to sRGB
converted = ImageCms.profileToProfile(image, icc_profile, srgb_profile, outputMode="RGB")

# Save the image with an embedded sRGB profile
converted.save(output_image_path, "JPEG", icc_profile=srgb_profile.tobytes())

print("ICC profile applied and image saved as:", output_image_path)
