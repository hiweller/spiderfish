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

# ap = argparse.ArgumentParser()
# ap.add_argument("-d", "--dataset", required = True,
# 	help = "Path to the directory that contains the images to be indexed")
# args = vars(ap.parse_args())

# folderPath = args["dataset"]
folderPath = '.'

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

# # for pic in checkOneStrict:
# # 	src = folderPath + '/' + pic[1]
# # 	dst = folderPath + '/Pass/' + pic[1]
# # 	copyfile(src, dst)

# # for pic in checkTwoPass:
# # 	src = folderPath + '/' + pic[1]
# # 	dst = folderPath + '/Pass/' + pic[1]
# # 	copyfile(src, dst)

# # for pic in checkTwoFail:
# # 	src = folderPath + '/' + pic[1]
# # 	dst = folderPath + '/Fail/' + pic[1]
# # 	copyfile(src, dst)

# print "Strict pass"
# for img in checkOneStrict:
# 	pic = img[0]
# 	f, axarr = plt.subplots(2)
# 	imname = folderPath+'/'+img[1]
# 	image = cv2.imread(imname)
# 	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# 	axarr[0].plot(pic[0], 'r-', pic[1], 'b-', img[2], 'm-')
# 	axarr[1].imshow(image)
# 	# plt.imshow(image)
# 	ctrcorr=[]
# 	for vec in pic[0:4]:
# 		ctrcorr.append(np.corrcoef(vec, pic[4])[1,0])
# 	# ctrcorr = np.triu(np.corrcoef(pic))
# 	print ctrcorr
# 	plt.title("Pass")
# 	# plt.savefig('Out/'+img[1][0:8]+'_StrictPass.png')
# 	plt.show()
# 	# plt.close("all")

# print "Soft pass"
# for img in checkTwoPass:
# 	pic = img[0]
# 	f, axarr = plt.subplots(2)
# 	imname = folderPath+'/'+img[1]
# 	image = cv2.imread(imname)
# 	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# 	axarr[0].plot(pic[0], 'r-', pic[1], 'b-', img[2], 'm-')
# 	axarr[1].imshow(image)
# 	ctrcorr=[]
# 	for vec in pic[0:4]:
# 		ctrcorr.append(np.corrcoef(vec, pic[4])[1,0])
# 	# ctrcorr = np.triu(np.corrcoef(pic))
# 	print ctrcorr
# 	plt.title("Pass")
# 	# plt.savefig('Out/'+img[1][0:8]+'_StrictPass.png')
# 	plt.show()
# 	# plt.close("all")

print "Pass"

for img in checkOneStrict:
	pic = img[0]
	ctrcorr=img[2]
	
	if np.mean(ctrcorr) <= 1: #and max(ctrcorr) <= maxCtr:
		f, axarr = plt.subplots(2)
		imname = folderPath+'/'+img[1]
		image = cv2.imread(imname)
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		axarr[0].plot(pic[0], 'r-', pic[1], 'b-', pic[4], 'm-')
		axarr[1].imshow(image)
	# plt.imshow(image)

	# ctrcorr = np.triu(np.corrcoef(pic))
		print np.mean(ctrcorr), max(ctrcorr)
		plt.title("Fail")
	# plt.savefig('Out/'+img[1][0:8]+'_StrictPass.png')
		plt.show()
	# plt.close("all")

for img in checkTwoPass:
	pic = img[0]
	ctrcorr=img[2]
	
	if np.mean(ctrcorr) <= 1: #and max(ctrcorr) <= maxCtr:
		f, axarr = plt.subplots(2)
		imname = folderPath+'/'+img[1]
		image = cv2.imread(imname)
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		axarr[0].plot(pic[0], 'r-', pic[1], 'b-', pic[4], 'm-')
		axarr[1].imshow(image)
	# plt.imshow(image)

	# ctrcorr = np.triu(np.corrcoef(pic))
		print np.mean(ctrcorr), max(ctrcorr)
		plt.title("Fail")
	# plt.savefig('Out/'+img[1][0:8]+'_StrictPass.png')
		plt.show()
	# plt.close("all")

print "Fail"
for img in checkTwoFail:
	pic = img[0]
	ctrcorr=img[2]
	
	if np.mean(ctrcorr) <= 1: #and max(ctrcorr) <= maxCtr:
		f, axarr = plt.subplots(2)
		imname = folderPath+'/'+img[1]
		image = cv2.imread(imname)
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		axarr[0].plot(pic[0], 'r-', pic[1], 'b-', pic[2], 'y-', pic[3], 'g-', pic[4], 'm-')
		axarr[1].imshow(image)
	# plt.imshow(image)

	# ctrcorr = np.triu(np.corrcoef(pic))
		print np.mean(ctrcorr), max(ctrcorr)
		plt.title("Fail")
	# plt.savefig('Out/'+img[1][0:8]+'_StrictPass.png')
		plt.show()
	# plt.close("all")
# 	# plt.show()

# # for pic in checkOneFail:
# # 	temp = np.triu(np.corrcoef(pic[0]))
# # 	temp = temp[0][1:4], temp[1][2:4], temp[2][3:4]
# # 	temp = [i for j in temp for i in j]
# # 	imname = 'Opistognathidae/'+pic[1] 
# # 	image = cv2.imread(imname)
# # 	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# # 	plt.imshow(image)
# # 	plt.title("Fail")
# # 	print pic[1]
# # 	print sorted(temp)
# # 	plt.show()

# # for pic in checkOneSoft:
# # 	temp = np.triu(np.corrcoef(pic[0]))
# # 	temp = temp[0][1:4], temp[1][2:4], temp[2][3:4]
# # 	temp = [i for j in temp for i in j]
# # 	imname = 'Opistognathidae/'+pic[1] 
# # 	image = cv2.imread(imname)
# # 	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# # 	plt.imshow(image)
# # 	plt.title("Soft")
# # 	print pic[1]
# # 	print sorted(temp)
# # 	plt.show()

# # for img in checkOneSoft:
# #     imname = 'Opistognathidae/'+img[1] 
# #     image = cv2.imread(imname)
# #     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# #     plt.imshow(image)
# #     plt.title("Soft")
# #     plt.show()

# # for img in checkOneFail:
# #     imname = 'Opistognathidae/'+img[1] 
# #     image = cv2.imread(imname)
# #     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# #     plt.imshow(image)
# #     plt.title("Fail")
# #     plt.show()



# # neg = []
# # # for imagePath in glob.glob(args["dataset"] + "/*.jpg"):
# # for imagePath in negative:

# # 	imageID = imagePath[imagePath.rfind("/") + 1:]
# # 	image = cv2.imread(imagePath)
# # 	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# # 	# describe image
# # 	features = cd.describe(image)
# # 	neg.append(features)

# # for f in features:


# # negative = ['Opistognathidae/opvar_u3.jpg', 'Opistognathidae/opnig_u0.jpg', 'Opistognathidae/opexi_u1.jpg', 'Opistognathidae/opmac_u2.jpg', 'Opistognathidae/opexi_u0.jpg', 'Opistognathidae/oprho_u1.jpg', 'Opistognathidae/oprho_u3.jpg', 'Opistognathidae/opvar_u3.jpg', 'Opistognathidae/opwhi_u1.jpg']

# # middle = ['Opistognathidae/opalb_u0.jpg', 'Opistognathidae/opaur_u1.jpg', 'Opistognathidae/opcya_u0.jpg', 'Opistognathidae/opaur_u2.jpg', 'Opistognathidae/opcas_u0.jpg', 'Opistognathidae/opden_j0.jpg', 'Opistognathidae/opden_u0.jpg', 'Opistognathidae/opmac_u1.jpg', 'Opistognathidae/opran_u4.jpg', 'Opistognathidae/oprho_j0.jpg', 'Opistognathidae/oprho_u0.jpg', 'Opistognathidae/oprob_u1.jpg', 'Opistognathidae/opros_f0.jpg', 'Opistognathidae/opros_m0.jpg', 'Opistognathidae/oprho_u0.jpg', 'Opistognathidae/opruf_u1.jpg', 'Opistognathidae/opsem_u0.jpg', 'Opistognathidae/stdav_u0.jpg', 'Opistognathidae/oprho_u1.jpg']

# # # positive = ['Opistognathidae/opmex_u0.jpg', 'Opistognathidae/opgal_u0.jpg', 'Opistognathidae/ophon_u0.jpg', 'Opistognathidae/oplat_u0.jpg']
# # positive = ['Opistognathidae/opmex_u0.jpg', 'Opistognathidae/opgal_u0.jpg', 'Opistognathidae/ophon_u0.jpg', 'Opistognathidae/oplat_u0.jpg', 'Opistognathidae/lohig_u0.jpg', 'Opistognathidae/lolem_u0.jpg', 'Opistognathidae/lomic_u0.jpg', 'Opistognathidae/losin_u0.jpg', 'Opistognathidae/opcas_u1.jpg', 'Opistognathidae/opcra_u0.jpg', 'Opistognathidae/opdar_u0.jpg', 'Opistognathidae/opeve_u1.jpg', 'Opistognathidae/ophop_u0.jpg', 'Opistognathidae/oplon_u1.jpg', 'Opistognathidae/opnig_u1.jpg', 'Opistognathidae/opnig_u2.jpg', 'Opistognathidae/opnig_u3.jpg', 'Opistognathidae/oppan_m0.jpg', 'Opistognathidae/oppan_u0.jpg', 'Opistognathidae/oppan_u1.jpg', 'Opistognathidae/oppap_u0.jpg', 'Opistognathidae/opran_u0.jpg', 'Opistognathidae/opran_u1.jpg', 'Opistognathidae/opran_u2.jpg', 'Opistognathidae/opran_u3.jpg', 'Opistognathidae/oprho_u2.jpg', 'Opistognathidae/oprob_u0.jpg', 'Opistognathidae/opros_j0.jpg', 'Opistognathidae/opsco_u0.jpg', 'Opistognathidae/opsol_u0.jpg', 'Opistognathidae/opvar_u0.jpg', 'Opistognathidae/opvar_u1.jpg', 'Opistognathidae/opvar_u2.jpg', 'Opistognathidae/opwhi_u0.jpg', 'Opistognathidae/opwhi_u2.jpg', 'Opistognathidae/stdic_u0.jpg', 'Opistognathidae/stere_u0.jpg', 'Opistognathidae/stimm_u0.jpg', 'Opistognathidae/stshe_u0.jpg', 'Opistognathidae/stver_u0.jpg']


# # # open output
# # # output = open(args["index"], "w")

# # neg = []
# # pos = []
# # mid = []

# # # loop over images
# # # for imagePath in glob.glob(args["dataset"] + "/*.jpg"):
# # for imagePath in negative:

# # 	imageID = imagePath[imagePath.rfind("/") + 1:]
# # 	image = cv2.imread(imagePath)
# # 	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# # 	# describe image
# # 	features = cd.describe(image)
# # 	neg.append(features)

# # for imagePath in middle:

# # 	imageID = imagePath[imagePath.rfind("/") + 1:]
# # 	image = cv2.imread(imagePath)
# # 	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


# # 	# describe image
# # 	features = cd.describe(image)
# # 	mid.append(features)

# # for imagePath in positive:

# # 	imageID = imagePath[imagePath.rfind("/") + 1:]
# # 	image = cv2.imread(imagePath)
# # 	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


# # 	# describe image
# # 	features = cd.describe(image)
# # 	pos.append(features)


# # # posCoeff = []

# # # for pic in pos:
# # # 	temp = np.corrcoef(pic)
# # # 	temp = temp[0][1:4], temp[1][2:4], temp[2][3:4]
# # # 	temp = [i for j in temp for i in j]
# # # 	posCoeff.append(temp)
# # p = 0
# # m = 0
# # n = 0

# # sumpos = []
# # summid = []
# # sumneg = []
# # thresh = 0.5

# # for pic in pos:
# # 	# f, axarr = plt.subplots(2)
# # 	# img = cv2.imread(positive[p])
# # 	# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# # 	# axarr[0].plot(pic[0], 'r-', pic[1], 'g-', pic[2], 'b-', pic[3], 'm-')
# # 	# axarr[1].imshow(img)
# # 	# plt.title("Positive")
# # 	# plt.savefig(positive[p][16:24]+'.png')
# # 	# # plt.show()
# # 	# plt.close("all")
# # 	temp = []
# # 	for corner in pic:
# # 		temp.append(sum(np.logical_and(corner >= max(corner)-thresh, corner <= max(corner))))
# # 	sumpos.append(temp)

# # 	p = p + 1

# # for pic in mid:
# # 	# f, axarr = plt.subplots(2)
# # 	# img = cv2.imread(middle[m])
# # 	# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# # 	# axarr[0].plot(pic[0], 'r-', pic[1], 'g-', pic[2], 'b-', pic[3], 'm-')
# # 	# axarr[1].imshow(img)
# # 	# plt.title("Middle")
# # 	# plt.savefig(middle[m][16:24]+'.png')
# # 	# plt.close("all")
# # 	temp = []
# # 	for corner in pic:
# # 		temp.append(sum(np.logical_and(corner >= max(corner)-thresh, corner <= max(corner))))
# # 	summid.append(temp)
# # 	m = m + 1
# # 	# plt.show()

# # for pic in neg:
# # 	# f, axarr = plt.subplots(2)
# # 	# img = cv2.imread(negative[n])
# # 	# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# # 	# axarr[0].plot(pic[0], 'r-', pic[1], 'g-', pic[2], 'b-', pic[3], 'm-')
# # 	# axarr[1].imshow(img)
# # 	# plt.title("Negative")
# # 	# plt.savefig(negative[n][16:24]+'.png')
# # 	# plt.close("all")
# # 	temp = []
# # 	for corner in pic:
# # 		temp.append(sum(np.logical_and(corner >= max(corner)-thresh, corner <= max(corner))))
# # 	sumneg.append(temp)
# # 	n = n + 1
# # 	# plt.show()

# # 	# temp = kruskalwallis(features[0:len(features)])
# # 	# kw.append((imageID, temp[0], temp[1]))

# # 	# kw = [str(f) for f in kw]
# # 	# output.write("%s, %s\n" % (imageID, ",".join(kw)))	
# # 	# features = [str(f) for f in features]
# # 	# output.write("%s, %s\n" % (imageID, ",".join(features)))

# # names = ["Positive", "Middle", "Negative"]
# # j = 0
# # for i in [sumpos, summid, sumneg]:
# # 	print "Mean " + str(np.mean(i)) 
# # 	print names[j]
# # 	j = j + 1
# # 	for row in i:
# # 		print row

# # # In [203]: np.logical_and(corner >= thresh, corner <= 0.8)

# # # print sumpos
# # # print summid
# # # print sumneg

# # # output = open(args["index"], "w")

# # # # order by 
# # # kw = sorted(kw, key=lambda l:l[1])

# # # with open(args["index"], 'wb') as f:
# # # 	wr = csv.writer(f)
# # # 	wr.writerows(kw)