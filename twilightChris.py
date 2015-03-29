#\ls 10C.BIAS.0* > list_of_bias_frames
 
#to launch the code: python ccd2.py <directory> <list of fits files>
import sys
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import math
 
 
#-----------------------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------------------
 
def get_stats(temp_data):
    mu = np.mean(temp_data)
    sigma = np.std(temp_data)
    return mu, sigma
 
def make_bins(temp_data, bin_width):
    max = np.max(temp_data)
    min = np.min(temp_data)
    return np.floor((max - min)/bin_width)
     
def make_gaussian(temp_data, bin_width):    
    mu, sigma = get_stats(temp_data)
     
    #For domain
    min = np.min(temp_data)
    max = np.max(temp_data)
    x = np.arange(min, max, bin_width)
 
    #Coefficient for the normalized gaussian
    a = 1/(sigma * math.sqrt(2 * math.pi))
     
    #For gaussian scaling
    temp_data_size = temp_data.size
     
    #Create the scaled gaussian curve. Scales by bin_width * array_size
    gaussian = bin_width * temp_data_size * a * np.exp(-np.power(x - mu,2.)/(2. * np.power(sigma,2.)))
     
    return x, gaussian
     
     
def mask_data(temp_data, n_sigma):
    done_masking = False
     
    while done_masking == False:
     
        temp_data_size_before = temp_data[np.isnan(temp_data[:]) == False].size
        mu, sigma = get_stats(temp_data[np.isnan(temp_data[:]) == False])
        temp_data[temp_data[:] > mu + n_sigma*sigma] = np.NaN
        temp_data[temp_data[:] < mu - n_sigma*sigma] = np.NaN
        temp_data_size_after = temp_data[np.isnan(temp_data[:]) == False].size
        if (temp_data_size_before == temp_data_size_after):
            done_masking = True
         
    temp_data[np.isnan(temp_data[:]) == False] = 1
    temp_data[np.isnan(temp_data[:]) == True] = 0
     
    print '\t','mu: ', mu
    print '\t','sigma: ', sigma
    return temp_data, mu, sigma
     
#FITS directory
directory = sys.argv[1]
 
#-----------------------------------------------------------------------------------------
# Bias Frames
#-----------------------------------------------------------------------------------------
 
#List of bias FITS files
bias_fits_list = sys.argv[2]
 
#Open list of bias FITS files, count how many are in the list, and close the list.
opened_bias_fits_list = open(directory+bias_fits_list)
bias_counter = 0
for line in opened_bias_fits_list:
    bias_counter += 1
opened_bias_fits_list.close()
 
#Create an array of the size bias_counter for averaging all the bias frames
bias_count = np.zeros(bias_counter)
 
#counter
i = 0
 
#Open list of bias FITS files. For each path appended FITS file in the list...
opened_bias_fits_list = open(directory+bias_fits_list)
for line in opened_bias_fits_list:
 
    #path to bias FITS file
    bias_fits_file = directory+line
    print bias_fits_file
 
    #Open the bias FITS file
    hdulist = fits.open(bias_fits_file)
 
    #Print exposure time.
    print '\t', 'Exposure time: ', hdulist[0].header['exptime']
 
    #Read in image data into a 1D array
    data = hdulist[0].data
    masked_data = np.copy(data) 
 
    #Get statistics from the data, clip outliers, and re calculate statistics
    n_sigma = 2
    masked_data, mu, sigma = mask_data(masked_data, n_sigma)
         
    #Final data is the data multiplied by the mask
    final_data = masked_data * data
 
    #Plot histogram of final data with gaussian overlay
    final_data_1D = final_data[[final_data[:] != 0]].reshape(-1,1)
    fig = plt.figure()          
    bin_width = 1
    bins = make_bins(final_data_1D, bin_width)
    plt.hist(final_data_1D, bins)   
     
    x, gaussian = make_gaussian(final_data_1D, bin_width)   
    plt.plot(x, gaussian)
 
    plt.title(line)
    plt.xlabel('Count')
    plt.ylabel('Number of Pixels')
    fig.show()
    plt.savefig(line + ".png")
    raw_input()
    plt.close()
 
    #Close the bias FITS file
    hdulist.close()
     
 
#Close the list of bias FITS files
opened_bias_fits_list.close()
 
 
 
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#flag clipped pixels and divide by that many fewer in the average
#averages biases by adding and dividing 
#
#take the median of each stacked pixel
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 
 
 
#Create a primary HDU to encapsulate the data
hdu = fits.PrimaryHDU(dark_array)
 
#Create the HDU list
hdulist = fits.HDUList([hdu])
hdulist.writeto("avg_dark_current.fit", clobber = True)
 
#Open averaged dark fits and plot.
hdulist = fits.open("avg_dark_current.fit")
hdulist.close()
 
quit()
 
 
 
 
 
 
# 65535