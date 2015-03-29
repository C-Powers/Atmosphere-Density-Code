import pyfits
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import datetime
import time
  
 #create an array of all of the filenames
import glob
files = glob.glob('ex_*.FIT')
  
#make a function to do some stats
def statsy(files, bias_data):
#take error for histogram for each image
    #import files
    hdulist = pyfits.open(files)
    data = hdulist[0].data
   # bias_data = bias_data
    
    print "bias_data", bias_data
 
    #get GMT times
    exptime = hdulist[0].header['EXPTIME']
    clock = hdulist[0].header['TIME-OBS']
    pt = datetime.datetime.strptime(clock,'%H:%M:%S.%f')
    total_sec = pt.second+pt.minute*60+pt.hour*3600
    print "GMT (sec)", total_sec
     
    #counts per second per pixel
    #cpsPixel = data/exptime - dark_current
    cpsPixel = (data - bias_data)/exptime
   # cpsPixel = data/exptime
    print "cps/pixel", cpsPixel #cps per pixel


    #mean and median of the cps/pixel
    mean = np.mean(cpsPixel)
    median = np.median(cpsPixel)
    print "mean cps", mean
    print "type mean", type(mean)
    print "median cps", median   
     
    #std of the mean
    stdMean = stats.sem(cpsPixel, ddof=len(cpsPixel)-1)
    #stdMean = np.float(stdMean)
    print "type(stdMean)", type(stdMean)
    print "std of the mean", stdMean
 
    return mean, median, exptime, total_sec, stdMean
  
#---------------------------------------------------------------------------------------- 
mean_cps = []
median_cps = []
time=[]
clocky=[]
stdMean_cps=[]
 
bdata = pyfits.open('final_bias.fit')
bias_data = bdata[0].data
bdata.close()
  
for i, value in enumerate(files):
    #create an array that adds the mean value of the cps/pixel for each image
    mean, median, exptime, total_sec, stdMean = statsy(files[i], bias_data) 
    mean_cps.append(mean)
    median_cps.append(median)
    time.append(exptime)
    clocky.append(total_sec)
    stdMean_cps.append(stdMean)
    #create an array the returns the exposure time
      
print "mean cps", mean_cps
print "median_cps", median_cps
print "stdMean_cps", stdMean_cps
print "time",time
print "clocky", clocky
  
stdMean_cps
 
fig1 = plt.figure()
plt.plot(clocky,mean_cps, '.', color = "green")
plt.errorbar(clocky, mean_cps, yerr=stdMean_cps, color = "red")
#plt.yscale('log')
plt.xlabel('Time')
plt.ylabel('Mean Count per Second')
plt.title("Experiment 1 - Mean")
plt.grid(True)
fig1.show()
plt.savefig("Mean.eps")
raw_input()
plt.close()
  
fig2 = plt.figure() 
plt.plot(clocky,median_cps, '-')
plt.yscale('log')
plt.xlabel('Time')
plt.ylabel('Median Count per Second')
plt.title("Experiment 1 - Median")
plt.grid(True)
fig2.show()
plt.savefig("Median.eps")
raw_input()
plt.close



#note, clip where rayleigh scattering becomes undominant