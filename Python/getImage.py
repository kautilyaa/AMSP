import numpy as np
import cv2

def getImage(datastream, save_path=None):
	arr = np.fromstring(datastream, np.uint8)
	img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
	return img
