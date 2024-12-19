from PIL import Image

# Open the JPG file
img = Image.open(r'C:\Users\proud\Documents\Code\BackendIOC\raw\test2.jpg')



# Save it as a TIFF file
img.save('test2.tiff', format='TIFF')
