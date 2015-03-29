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
      

hdulist = pyfits.open('ex_7.38_1.00000001.FIT')

dataI = hdulist[0].data.reshape(-1,1)





masked_data = np.copy(dataI)
masked_data = mask_data(masked_data, 3)

data = masked_data*dataI
print "dataI", dataI
print "masked_data", masked_data
print "data", data




mean = np.mean(data)
sigma = np.std(data)

xmin = mean - 2*sigma
xmax = mean + 2*sigma



#gaussian
binWidth = 5
xval = np.arange(xmin, xmax)
gauss = (binWidth*data.size)/(sigma*np.sqrt(2* np.pi)) * np.exp( - (xval-mean)**2 / (2*sigma**2))


#chi^2 test
#chisq, p = stats.chisquare(data, gauss, ddof = len(data)-1, axis=None)
#print chisq
#print p

print "mean", mean
print "RMS", sigma
xval = np.arange(xmin, xmax)
plt.hist(data, bins = range(np.min(data), np.max(data), binWidth))
plt.plot(xval, gauss,  linewidth=2, color = "red")
plt.title("Exposure time idk")
plt.xlabel("Counts")
plt.ylim(0, np.max(data))
plt.savefig('error.png')
plt.show()



