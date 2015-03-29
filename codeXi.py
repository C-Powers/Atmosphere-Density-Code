import pyfits
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.stats import chi2
import datetime
import time
  

def get_stats(temp_data):
    mu = np.mean(temp_data)
    sigma = np.std(temp_data)
    return mu, sigma
    
    
#Masks a data set by iteratively setting all values outside a multiple of sigma to NaN.
#Creates a mask by setting the final values to 1 and the final NaN's to 0.
#after mask made, multipy by data set, will give values and zeroes
def mask_data(temp_data, n_sigma):
    counter = 0
    done_masking = False
    while done_masking == False:
        temp_data_size_before = temp_data[np.isnan(temp_data[:]) == False].size
       # print '\t', 'temp_data_size_before:', temp_data_size_before
        mu, sigma = get_stats(temp_data[np.isnan(temp_data[:]) == False])
        temp_data[temp_data[:] > mu + n_sigma*sigma] = np.NaN
        temp_data[temp_data[:] < mu - n_sigma*sigma] = np.NaN
        temp_data_size_after = temp_data[np.isnan(temp_data[:]) == False].size
      #  print '\t', 'temp_data_size_after:', temp_data_size_after
 
        counter += 1
        if (temp_data_size_before == temp_data_size_after):
        	done_masking = True
 
    temp_data[np.isnan(temp_data[:]) == False] = 1
    temp_data[np.isnan(temp_data[:]) == True] = 0
    print '\t', 'counter:', counter
 
    print '\t','mu: ', mu
    print '\t','sigma: ', sigma
    return temp_data
   
  
#make a function to do some stats
def statsy(files, bias_data):
	#take error for histogram for each image
	#import files
	hdulist = pyfits.open(files)
	#data = hdulist[0].data.reshape(-1,1)
	#bias_data = bias_data.reshape(-1,1)

	data_noClip = hdulist[0].data

	n_sigma = 3

	print type(data_noClip)


	#get GMT times
	exptime = hdulist[0].header['EXPTIME']
	clock = hdulist[0].header['TIME-OBS']
	pt = datetime.datetime.strptime(clock,'%H:%M:%S.%f')
	total_sec = pt.second+pt.minute*60+pt.hour*3600 


	cpsPixel = (data_noClip - bias_data)/exptime
	
	
	masked_data = np.copy(cpsPixel)
	clip_img = mask_data(masked_data, 2)

	final_img = clip_img * cpsPixel

	#mean and median of the cps/pixel
	mean = np.mean(final_img[final_img[:]!=0])
	median = np.median(final_img)

	#std of the mean
	stdMean = stats.sem(final_img.reshape(-1), ddof=len(final_img)-1)

	return mean, median, exptime, total_sec, stdMean
  
#---------------------------------------------------------------------------------------- 


 #create an array of all of the filenames
import glob
files = glob.glob('*.FIT')
  
  
mean_cps = []
median_cps = []
time=[]
clocky=[]
stdMean_cps=[]
 
hdulist = pyfits.open('final_bias.fit')
bias_data = hdulist[0].data
hdulist.close()
  
print "QUIT", bias_data.shape, np.max(bias_data)
  
for i, value in enumerate(files):
	#create an array that adds the mean value of the cps/pixel for each image
	mean, median, exptime, total_sec, stdMean = statsy(files[i], bias_data) 
	mean_cps.append(mean)
	median_cps.append(median)
	time.append(exptime)
	clocky.append(total_sec)
	stdMean_cps.append(stdMean)
	#create an array the returns the exposure time
 
mean_cps = np.array(mean_cps)
median_cps = np.array(median_cps)
time = np.array(time)
clocky = np.array(clocky) - 8000
stdMean_cps = np.array(stdMean_cps)

  
#create a chi^2 fit
#numargs=chi2.numargs
#xi=chi2(mean_cps)


for i,value in enumerate(clocky):
	if clocky[i] >= 9250-8000:
		#clocky = 0
		#mean_cps= 0
		print "OUT OF RANGE"



 
fig0 = plt.figure()
plt.imshow(bias_data)
plt.colorbar()
fig0.show()
raw_input()
plt.close
 
fig1 = plt.figure()
plt.plot(clocky,mean_cps, '.', color = "green")
plt.errorbar(clocky, mean_cps, yerr=3*stdMean_cps, color = "red", fmt=None)
#plt.yscale('log')
plt.xlabel('Time')
plt.ylabel('Mean Count per Second')
plt.title("Experiment 1 - Mean")
plt.grid(True)
fig1.show()
plt.savefig("Mean.eps")
raw_input()
plt.close()