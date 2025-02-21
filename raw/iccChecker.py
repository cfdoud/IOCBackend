from PIL import ImageCms

icc_profile_path = r"C:\Windows\System32\spool\drivers\color\CameraProfile_New.icm"

try:
    icc_profile = ImageCms.getOpenProfile(icc_profile_path)
    print("ICC Profile loaded successfully!")
except Exception as e:
    print("Error loading ICC Profile:", e)
