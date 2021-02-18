# import the necessary packages
import argparse
import cv2
from PIL import Image as PIL_IMAGE
import numpy as np
import glob
import os
# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False

scale=2
image = []
path = ""
def transparentOverlay(src , overlay , pos=(0,0),scale = 1):
    """
    :param src: Input Color Background Image
    :param overlay: transparent Image (BGRA)
    :param pos:  position where the image to be blit.
    :param scale : scale factor of transparent image.
    :return: Resultant Image
    """
    overlay = cv2.resize(overlay,(0,0),fx=scale,fy=scale)
    h,w,_ = overlay.shape  # Size of foreground
    rows,cols,_ = src.shape  # Size of background Image
    y,x = pos[0],pos[1]    # Position of foreground/overlay image
    
    #loop over all pixels and apply the blending equation
    for i in range(h):
        for j in range(w):
            if x+i >= rows or y+j >= cols:
                continue
            alpha = float(overlay[i][j][3]/255.0) # read the alpha channel 
            src[x+i][y+j] = alpha*overlay[i][j][:3]+(1-alpha)*src[x+i][y+j]
    return src


def click_and_crop(event, x, y, flags, param):
	# grab references to the global variables
	global refPt, cropping
	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping is being
	# performed
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt = [(x, y)]
		cropping = True
	# check to see if the left mouse button was released
	elif event == cv2.EVENT_LBUTTONUP:
		# record the ending (x, y) coordinates and indicate that
		# the cropping operation is finished
		refPt.append((x, y))
		cropping = False
		# draw a rectangle around the region of interest
		cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
		cv2.imshow("image", image)
		

def load_and_paste(fname):
	global image, refPt, cropping, path
	image = cv2.imread(fname)
	full_image = image.copy()
	full_image = cv2.resize(full_image, (750*scale, 500*scale))
	clone = image.copy()
	clone = cv2.resize(clone,(750,500))
	image = cv2.resize(image,(750,500))
	cv2.namedWindow("image")
	cv2.setMouseCallback("image", click_and_crop)
	nxt = False
	# keep looping until the 'q' key is pressed
	while True:
		# display the image and wait for a keypress
		cv2.imshow("image", image)
		key = cv2.waitKey(1) & 0xFF
		# if the 'r' key is pressed, reset the cropping region
		if key == ord("r"):
			image = clone.copy()
		# if the 'c' key is pressed, break from the loop
		elif key == ord("n"):
			nxt = True
			break
		elif key == ord("p"):
			break
	print("broke", len(refPt), nxt)		
	# if there are two reference points, then crop the region of interest
	# from teh image and display it
	if len(refPt) == 2 and nxt == False:
		print("entered")
		x1, y1 = refPt[0]
		x2, y2 = refPt[1]
		width = abs(x1 - x2)
		height = abs(y1 - y2)
		full_width = width * scale
		full_height = height * scale
		logo = cv2.imread("logo.png",cv2.IMREAD_UNCHANGED)
		logor = cv2.resize(logo,(width, height))
		logo_full = cv2.resize(logo, (full_width, full_height))

		bg_img = clone.copy()

		pasted = transparentOverlay(bg_img,logor,(x1,y1))
		
		full_pasted = transparentOverlay(full_image, logo_full,(x1*scale, y1*scale))
		print("Writing", fname)

		cv2.imwrite("out/"+fname.replace("target/",""),full_pasted)
		cv2.imshow("ROI", pasted)
		
		cv2.waitKey(0)
	# close all open windows
	cropping = False
	refPt = []
	cv2.destroyAllWindows()

if __name__ == "__main__":
	path = os.getcwd()
	for f in glob.glob("target/*.JPG"):
		load_and_paste(f)

	
