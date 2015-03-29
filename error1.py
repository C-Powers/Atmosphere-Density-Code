import pyfits
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.stats import chi2
import datetime
import time
      
      
      

hdulistErr = pyfits.open('ex_7.38_1.00000001.FIT')

dataErr = hdulistErr[0].data.reshape(-1,1)



meanErr = np.mean(dataErr)
sigmaErr = np.std(dataErr)



xminErr = meanErr - 3*sigmaErr
xmaxErr = meanErr + 3*sigmaErr


#gaussian
binWidthErr = 1
xvalErr = np.arange(xminErr, xmaxErr)
gaussErr = (binWidthErr*dataErr.size)/(sigmaErr*np.sqrt(2* np.pi)) * np.exp( - (xvalErr-meanErr)**2 / (2*sigmaErr**2))


#chi^2 test
#chisq, p = stats.chisquare(data, gauss, ddof = len(data)-1, axis=None)
#print chisq
#print p

print "meanErr", meanErr
print "RMSErr", sigmaErr
xvalErr = np.arange(xminErr, xmaxErr)
plt.hist(dataErr, bins = range(np.min(dataErr), np.max(dataErr), binWidthErr))
plt.plot(xvalErr,gaussErr,  linewidth=2, color = "red")
plt.title("Exposure time idk")
plt.xlabel("Counts")
plt.savefig('error.png')
plt.show()