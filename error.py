import pyfits
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.stats import chi2
import datetime
import time
      
      
      

hdulist = pyfits.open('ex_7.21.00000001.FIT')

data = hdulist[0].data

mean = np.array(mean)
sigma = np.array(sigma)
data = np.array(data)


mean = np.mean(data)
sigma = np.std(data)
xmin = mean - 3*sigma
xmax = mean + 3*sigma

print type(mean)


binwidth = 1
xval = np.arange(xmin, xmax)
plt.hist(data, bins = range(np.min(data), np.max(data), binWidth)
#plt.plot(xval, (binWidth*data.size)/(sigma*np.sqrt(2* np.pi)) * np.exp( - (xval-mean)**2 / (2*sigma**2)), linewidth=2, color = "red"
#plt.show()