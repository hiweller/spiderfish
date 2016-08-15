# packages
import numpy as np
import cv2

""" 
Modified from: http://www.pyimagesearch.com/2014/12/01/complete-guide-building-image-search-engine-python-opencv/ (Adrian Rosebrock 2014)

Meant to examine corners of image and center of image to determine whether the image has one central object (fish) on a relatively uniform background. Basic idea is that if the four corners are similar to each other and relatively dissimilar to the center of the image it's probably a fish photograph with the fish filling most of the image.
"""
class ColorDescriptor:
	def __init__(self, bins):
		# store number of bins for histogram
		self.bins = bins

	def describe(self, image):
		# convert into HSV color space, initialize features
		image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
		features = []

		# get dimensions of image and compute center
		(h, w) = image.shape[:2]
		(cX, cY) = (int(w * 0.5), int(h * 0.5))

		# divide the image into four sections:
		segments = [(0, cX, 0, cY), (cX, w, 0, cY), (cX, w, cY, h), (0, cX, cY, h)]

		# make elliptical mask for center of image
		# WILL PROBABLY HAVE TO ADJUST THIS?
		(axesX, axesY) = (int(w * 0.8) / 2, int(h * 0.8) / 2)
		(smallX, smallY) = (int(w * 0.35) / 2, int(h * 0.35) / 2)
		ellipMask = np.zeros(image.shape[:2], dtype = "uint8")
		smallMask = np.zeros(image.shape[:2], dtype = "uint8")
		cv2.ellipse(ellipMask, (cX, cY), (axesX, axesY), 0, 0, 360, 255, -1)
		cv2.ellipse(smallMask, (cX, cY), (smallX, smallY), 0, 0, 360, 255, -1)

		# loop over the different corner segments
		for (startX, endX, startY, endY) in segments:
			# constructs a mask for each corner of the image with the elliptical center subtracted
			cornerMask = np.zeros(image.shape[:2], dtype = "uint8")
			cv2.rectangle(cornerMask, (startX, startY), (endX, endY), 255, -1)
			cornerMask = cv2.subtract(cornerMask, ellipMask)

			# extract a color histogram from the image and add to feature vector
			hist = self.histogram(image, cornerMask)
			# features = zip(features, hist)
			features.append(hist)
			# features.extend(hist)

		# extract color histogram from elliptical region, update feature vector
		hist = self.histogram(image, smallMask)
		features.append(hist)

		return features


	def histogram(self, image, mask):
		# extract a 3D HSV color histogram from the masked region of the image, then normalize it
		hist = cv2.calcHist([image], [0, 1, 2], mask, self.bins, [0, 180, 0, 256, 0, 256])
		hist = cv2.normalize(hist).flatten() # represents relative percentages (scale-free rather than resolution dependent)

		return hist













