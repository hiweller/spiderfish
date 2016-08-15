from colordescriptor import ColorDescriptor
import argparse
import glob
import cv2
import json
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from shutil import copyfile

"""
Indexes a set of images by corner and center using a HSV color histogram and stores indices in 'features' object. Requires colordescriptor.py.
"""

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required = True,
	help = "Path to the directory that contains the images to be indexed")
args = vars(ap.parse_args())

folderPath = args["dataset"]

if not os.path.exists(folderPath + '/Pass'):
	os.makedirs(folderPath + '/Pass')
if not os.path.exists(folderPath + '/Fail'):
	os.makedirs(folderPath + '/Fail')

# initialize the color descriptor
cd = ColorDescriptor((8, 12, 3)) # HSV binning -- 8 hue, 12 saturation, 3 value

features = []
ctrcorr = []
images = glob.glob(folderPath+'/*.jpg')

for pic in images:

	image = cv2.imread(pic)
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	ctr = []

	temp = cd.describe(image)
	features.append(temp)

	for i in temp[0:4]:
		ctr.append(np.corrcoef(i, temp[4])[1,0])
	ctrcorr.append(ctr)




names = [t[t.rfind("/")+1:] for t in images]

zippy = zip(features, names, ctrcorr)

""" Perform 2 checks: 
1) How many peaks are there within a certain range of the first peak? Uniform background will have relatively few high peaks while variable background will have many lower peaks and no strong signals. Measure by counting the number of peaks within some threshold below the highest peak [peak-thresh:peak].
2) Of those without a single strong peak, are the four corners extremely similar? Measure using correlation coefficients between four corners. If at least two are above the threshold then we have at least two pairs of corners that are extremely similar (usually top two and bottom two). If # (corrcoef >= 0.9) >= 2 then keep image.
Take images that passed one of two checks and copy them to a 'Keep' folder within current WD; put remaining images in a 'Reject' folder - can be accessed later to check for any missing images. 
"""

# CHECK ONE
checkOneStrict = []
checkOneSoft = []
checkOneFail = []
ctrCorr = []
peakThresh = 0.5

strictMean = 1.5
softMean = 4

baseCtr = 0.9
strictCtr = 0.25
softCtr = 0.11
maxCtr = 0.15

softCorr = 0.8
failCorr = 0.9

for pic in zippy:

	vec = pic[0]
	ctrcorr = pic[2]
	temp = []

	for corner in vec[0:4]:
		temp.append(sum(np.logical_and(corner >= max(corner)-peakThresh, corner <= max(corner))))

	if np.mean(temp) <= strictMean and max(ctrcorr) <= 0.998:
		checkOneStrict.append(pic)
	elif strictMean < np.mean(temp) <= softMean and np.mean(ctrcorr) <= strictCtr:
		checkOneSoft.append(pic)
	else:
		checkOneFail.append(pic)


# CHECK TWO
checkTwoPass = []
checkTwoFail = []

for pic in checkOneSoft:
	ctrcorr = pic[2]
	temp = np.triu(np.corrcoef(pic[0]))
	temp = temp[0][1:4], temp[1][2:4], temp[2][3:4]
	temp = [i for j in temp for i in j]

	if max(temp) >= softCorr and np.mean(ctrcorr) <= strictCtr:
		checkTwoPass.append(pic)
	elif np.mean(ctrcorr) <= softCtr:
		checkTwoPass.append(pic)
	else:
		checkTwoFail.append(pic)

for pic in checkOneFail:
	ctrcorr = pic[2]
	temp = np.triu(np.corrcoef(pic[0]))
	temp = temp[0][1:4], temp[1][2:4], temp[2][3:4]
	temp = [i for j in temp for i in j]
	temp = sorted(temp, reverse=True)[0:2]
	# temp = max(temp)

	if all(i >= failCorr for i in temp) and np.mean(ctrcorr) <= strictCtr and max(ctrcorr) <= maxCtr:
	# if temp >= failCorr:
		checkTwoPass.append(pic)
	elif np.mean(ctrcorr) <= softCtr and max(ctrcorr) <= 0.995:
		checkTwoPass.append(pic)
	else:
		checkTwoFail.append(pic)


for pic in checkOneStrict:
	src = folderPath + '/' + pic[1]
	dst = folderPath + '/Pass/' + pic[1]
	copyfile(src, dst)

for pic in checkTwoPass:
	src = folderPath + '/' + pic[1]
	dst = folderPath + '/Pass/' + pic[1]
	copyfile(src, dst)

for pic in checkTwoFail:
	src = folderPath + '/' + pic[1]
	dst = folderPath + '/Fail/' + pic[1]
	copyfile(src, dst)