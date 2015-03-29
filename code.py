
import pyfits
import numpy as np
import matplotlib.pyplot as plt

#create an array of all of the filenames
import glob
files = glob.glob('Desktop/Physics_136/Observe1/experiment/official/*.FIT')

#do i need this? no
filesarray=np.array(files)
array=np.arange(len(files))

#make a function to do some stats
def stats(files):
#take error for histogram for each image
	hdulist = pyfits.open(files)
	data = hdulist[0].data.reshape(-1,1)
	exptime = hdulist[0].header['EXPTIME']
	cpsPixel = data/exptime
	print "cps/pixel", cpsPixel #cps per pixel
	mean = np.mean(cpsPixel)
	print mean
	return mean, exptime

out_cps = [0]
time=[0]
for i, value in enumerate(files):
	#create an array that adds the mean value of the cps/pixel for each image
	mean, exptime = stats(files[i]) 
	out_cps.append(mean)
	time.append(exptime)
	#create an array the returns the exposure time
	

print out_cps
print time

plt.plot(time,out_cps, '-')
plt.yscale('log')
plt.show()