from PIL import Image

# Open the JPG file
img = Image.open(r'C:\Users\proud\Documents\Code\BackendIOC\raw\NewCam.jpg')



# Save it as a TIFF file
img.save('NewCam.tiff', format='TIFF')
