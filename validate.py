import os
import cv
import cv2
import sys
import copy
import numpy 
import datetime
from multiprocessing import Pool, cpu_count

def averageImage(image):
	# average all the light values
	return image.sum()/(image.size*1.0)

def validateFrame(args):
	# compare the average light values for the entire image and the sub image
	frameData, x, y, r = args
	frameAverage = averageImage(frameData)
	target = frameData[x-r:x+r+1, y-r:y+r+1]
	targetAverage = averageImage(target)
	return frameAverage < targetAverage

def validateVideo(videoName):
	threadPool = Pool(cpu_count())
	count = 0
	vidData = []
	radius = 1

	print 'loading %s.txt'%videoName

	# read the location data 
	with open('%s.txt'%videoName) as dataFile:
		data = dataFile.readlines()

	# get the coords from the string 
	coords = [[int(s) for s in x.split() if s.isdigit()] for x in data]

	print 'loading %s.mp4'%videoName

	# load the capture object
	vidcap = cv2.VideoCapture('%s.mp4'%videoName)

	# get the frames per second
	fps = int(vidcap.get(cv2.cv.CV_CAP_PROP_FPS))

	# load the frames of the video as long as there are coords
	success,image = vidcap.read()
	notFailed = True

	while success and count < len(coords):
		y, x = coords[count]
		greyFrame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		vidData += [[copy.deepcopy(greyFrame),x,y,radius]]
		count += 1
		success,image = vidcap.read()

	print 'Loaded %i frames from %s.mp4'%(len(vidData), videoName)

	# map the validation task to sub processes
	result = threadPool.map(validateFrame,vidData)

	# delete an existing result file
	try:
		os.remove('%s_result.txt'%videoName)
	except:
		# no existing file
		pass

	# write out the failures to the result file
	failCount = 0
	outFileName = '%s_result.txt'%videoName
	with open(outFileName,'a') as outFile:
		for i, state in enumerate(result):
			if not state:
				failCount += 1
				outFile.write('%s \n'%datetime.timedelta(seconds=i*1.0/fps))

	print '%i failures written to %s'%(failCount, outFileName)


if __name__ == '__main__':
	validateVideo(sys.argv[1])

