#!/usr/bin/python
# This is an iris matching program by Phil Kaiser-Parlette, based on an iris recognition project by Jorge Palacios
# (https://github.com/pctroll/computer-vision/tree/master/iris_recognition). The two major modifications of the
# original code are the editing of the normalization process and the addition of an image comparison process.
# Using OpenCV, it resizes the images, finds and colors in the pupils of the two eyes, converts them to grayscale,
# and creates histograms based on the new images. The histograms are then compared based on correlation, with a
# correlation of at least 75% resulting in a match, a correlation of at least 30% but below 75% resulting in a
# failure to match but allowing for a single extra attempt, and a correlation less than 30% resulting in a failure
# to match with no extra attempts given.
#
# To call this program, the user must include the full paths to the input eye and the database eye, in that order,
# as string arguments (within single or double quotes). If another attempt is given, the user must input the full
# path of the second input eye as a string when prompted.

import cv
import sys

# Returns the same image with the pupil masked black. It uses the FindContours 
# function to find the pupil, given a range of black tones. It then colors
# in the pupil and returns the new image.
# @param image		Original image for testing
# @returns image	Image with black-painted pupil

def fillPupil(frame):
	# create empty pupil image and obtain range to search for pupil
	pupilImg = cv.CreateImage(cv.GetSize(frame), 8, 1)
	cv.InRangeS(frame, (30,30,30), (80,80,80), pupilImg)
	# find contours of the pupil and store them in memory
	contours = cv.FindContours(pupilImg, cv.CreateMemStorage(0), mode = cv.CV_RETR_EXTERNAL)
	# erase and recreate pupil image
	del pupilImg
	pupilImg = cv.CloneImage(frame)
	# paint all pupil regions black and return new image
	while contours:
		moments = cv.Moments(contours)
		area = cv.GetCentralMoment(moments,0,0)
		if (area > 50):
			pupilArea = area
			pupil = contours
			cv.DrawContours(pupilImg, pupil, (0,0,0), (0,0,0), 2, cv.CV_FILLED)
			break
		contours = contours.h_next()
	return (pupilImg)

# Returns a histogram representation of the image, after first resizing it to 320 x 280,
# calling fillPupil to fill in the eye's pupil, and converting it to grayscale.
# @param string		String representing the full path of the image location
# @returns histogram	Histogram representation of the image after minor modifications
def getEyeHist(path):
	#get input eye and resize
	eye = cv.LoadImage(path)
	resizedEye = cv.CreateImage((320, 280), eye.depth, eye.channels)
	cv.Resize(eye, resizedEye)
	#fill pupil and convert to grayscale
	eyeFilled = fillPupil(resizedEye)
	grayEyeFilled = cv.CreateImage((eyeFilled.width, eyeFilled.height), eyeFilled.depth, 1)
	cv.CvtColor(eyeFilled, grayEyeFilled, cv.CV_BGR2GRAY)
	#obtain histogram representation of image
	hist = cv.CreateHist([10], cv.CV_HIST_ARRAY, [[0, 255]], 1)
	cv.CalcHist([grayEyeFilled], hist)
	return hist

# get input eye histogram
inputHist = getEyeHist(sys.argv[1])
# get database eye histogram
dbHist = getEyeHist(sys.argv[2])
# find match percentage
correlation = (cv.CompareHist(inputHist, dbHist, cv.CV_COMP_CORREL) * 100)
# normalize correlation (as negative is below no correlation)
if (correlation < 0.0):
	correlation = 0.0
# give proper output based on match percentage
if (correlation < 30.0):
	print "Match percentage", correlation, "%. Percentage is below automatic failure threshold (30%). Match unsuccessful."
elif (correlation >= 75.0):
	print "Match percentage", correlation, "%. Match successful."
# give second attempt
else:
	print "Match percentage", correlation, "%. Match unsuccessful. You have one attempt remaining."
	newInputPath = input("Please enter the path of the input eye: ")
	inputHist = getEyeHist(newInputPath)
	correlation = (cv.CompareHist(inputHist, dbHist, cv.CV_COMP_CORREL) * 100)
	if (correlation < 75.0):
		print "Match percentage", correlation, "%. Match unsuccessful."
	else:
		print "Match percentage", correlation, "%. Match successful."

