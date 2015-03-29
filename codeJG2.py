import pyfits
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import datetime
import time
from scipy.optimize import curve_fit
   
#Calculates mean and standard deviation of data
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
 
    data = hdulist[0].data
 
    #get GMT times
 
    exptime = hdulist[0].header['EXPTIME']
    print '\t','exptime', exptime
    clock = hdulist[0].header['TIME-OBS']
    print '\t','time:', clock
    pt = datetime.datetime.strptime(clock,'%H:%M:%S.%f')
    #subracting sunset time (in seconds) after 0:00 GMT
    total_sec = pt.second+pt.minute*60+pt.hour*3600 - 10159
    print '\t',"GMT (sec)", total_sec
 
    cpsPixel = (data - bias_data)/exptime
     
    masked_data = np.copy(cpsPixel)
    masked_data = mask_data(masked_data, 3)
 
    final_img = masked_data * cpsPixel
 
    #mean and median of the cps/pixel
    mean = np.mean(final_img[final_img[:]!=0])
    median = np.median(final_img)
    print '\t', "mean cps", mean
    #print '\t',"type mean", type(mean)
    print '\t',"median cps", median   
  
    #std of the mean
     
    stdMean = stats.sem(final_img.reshape(-1), ddof=len(final_img)-1)
    #print stdMean.shape
    #stdMean = np.float(stdMean)
    #print "type(stdMean)", type(stdMean)
    print '\t',"std of the mean", stdMean
 
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
clocky = np.array(clocky)
#clocky = np.array(clocky) - 6559
stdMean_cps = np.array(stdMean_cps)
  
 
#Clip the data so all exposure times are greater than 1 second (10 min before sunset)
#clipped_time = time[time[:] >= 1.0]
#clipped_index = time.size - clipped_time.size
#clipped_mean_cps = mean_cps[clipped_index:]
#clipped_clocky = clocky[clipped_index:]
#clipped_stdMean_cps = stdMean_cps[clipped_index:]
 
clipped_clocky = clocky[clocky[:] >= 0]
clipped_index = clocky.size - clipped_clocky.size
clipped_mean_cps = mean_cps[clipped_index:]
clipped_stdMean_cps = stdMean_cps[clipped_index:]
 
#Clip data so all times are before 10 minutes after sunset
clipped_clocky = clipped_clocky[clipped_clocky[:] <= 250]
clipped_mean_cps = clipped_mean_cps[0:clipped_clocky.size]
clipped_stdMean_cps = clipped_stdMean_cps[0:clipped_clocky.size]
 
log_clipped_mean_cps = np.log(clipped_mean_cps)
m, b = np.polyfit(clipped_clocky, log_clipped_mean_cps,1)
print m, b
fit = m*clipped_clocky + b
 
 
 
#Show the bias
fig0 = plt.figure()
plt.imshow(bias_data)
plt.colorbar()
fig0.show()
raw_input()
plt.close
  
#Plot the data with error bars
fig1 = plt.figure()
plt.plot(clipped_clocky, fit, '.', color="teal")
#plt.plot(clocky,mean_cps, '.', color = "green")
plt.plot(clipped_clocky,log_clipped_mean_cps, '.',  color = "green")
plt.errorbar(clipped_clocky, clipped_mean_cps, yerr=clipped_stdMean_cps,fmt = None,color = "red")
#plt.yscale('log')
plt.xlabel('Time')
plt.ylabel('Mean Count per Second')
plt.title("Experiment 1 - Mean")
plt.grid(True)
fig1.show()
plt.savefig("Mean.eps")
raw_input()
plt.close()