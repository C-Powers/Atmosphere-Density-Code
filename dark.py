#\ls 10C.dark.0* > list_of_dark_frames
 
#to launch the code: python twilight.py <directory> <list of dark fits files>
#Error:some of the pixels in the summed_masked_dark have values of 0
#Causing a divide by 0 error for the final dark.
 
import sys
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import math
 
 
#-----------------------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------------------
 
def make_bins(temp_data, bin_width):
    max = np.max(temp_data)
    min = np.min(temp_data)
    print '\t', 'max:', max
    print '\t', 'min:', min
    return np.ceil((max - min)/bin_width)
 
def get_stats(temp_data):
    mu = np.mean(temp_data)
    sigma = np.std(temp_data)
    return mu, sigma
 
#Makes a gaussian based on the data, it's mean, and it's sigma.
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
 
 
#Masks a data set by iteratively setting all values outside a multiple of sigma to NaN.
#Creates a mask by setting the final values to 1 and the final NaN's to 0.
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
    return temp_data
 
 
#Makes a stack by counting the files in a list, and reading the image size of a single file.
def make_stack(directory, list):
    opened_list = open(directory+list)
    counter = 0
    for line in opened_list:
        counter += 1
        a_fits_file = line
     
    hdulist = fits.open(directory+a_fits_file)
    columns  = hdulist[0].header['naxis1']
    rows =  hdulist[0].header['naxis2']
    hdulist.close()
 
    opened_list.close()
    return np.zeros((counter, rows, columns))
 
 
#-----------------------------------------------------------------------------------------
# dark Frames
#-----------------------------------------------------------------------------------------
#FITS directory
directory = sys.argv[1]
 
#List of dark FITS files
dark_fits_list = sys.argv[2]
 
#Open list of dark FITS FILES
opened_dark_fits_list = open(directory+dark_fits_list)
 
#Make 3D stack with dimensions: number of files in list, rows, columns
final_dark_stack = make_stack(directory,dark_fits_list)
masked_dark_stack = np.copy(final_dark_stack)
 
#Counter for the stack
list_count = 0
for line in opened_dark_fits_list:
     
    #path to dark FITS file
    dark_fits_file = directory+line
    print dark_fits_file
     
    #Open the dark FITS file
    hdulist = fits.open(dark_fits_file)
     
    #Print exposure time.
    exptime = hdulist[0].header['exptime']
    print '\t', 'Exposure time: ', exptime
     
    #Read in image data
    dark_data = hdulist[0].data/exptime
    masked_dark_data = np.copy(dark_data)
     
    #Masks data outside a multiple of sigma.
    n_sigma = 2
    masked_dark_data = mask_data(masked_dark_data, n_sigma)
     
    #Final data is the raw data multiplied by the mask
    final_dark_data = masked_dark_data * dark_data
     
    #Plot histogram of final data (without the zeros) with gaussian overlay
    final_dark_data_1D = final_dark_data[[final_dark_data[:] != 0]].reshape(-1,1)
    fig = plt.figure()
    bin_width = 1
    bins = make_bins(final_dark_data_1D, bin_width)
    plt.hist(final_dark_data_1D, bins)
     
    x, gaussian = make_gaussian(final_dark_data_1D, bin_width)
    plt.plot(x, gaussian)
     
    plt.title(line)
    plt.xlabel('Count')
    plt.ylabel('Number of Pixels')
    fig.show()
    #plt.savefig(line + ".png")
    raw_input()
    plt.close()
     
    #Close the dark FITS file
    hdulist.close()
     
    #Add the final data to the stack
    final_dark_stack[list_count,:,:] = final_dark_data
    masked_dark_stack[list_count,:,:] = masked_dark_data
     
    list_count += 1
 
#Close the list of dark FITS files
opened_dark_fits_list.close()
 
#Averages the final dark stack with the masked dark stack to create a single dark.
summed_final_dark = np.sum(final_dark_stack[:,:,:],0)
summed_masked_dark = np.sum(masked_dark_stack[:,:,:],0)
final_dark = summed_final_dark/summed_masked_dark
 
#Write final dark to FITS file
hdu = fits.PrimaryHDU(final_dark)
hdulist = fits.HDUList([hdu])
hdulist.writeto("final_dark.fit", clobber = True)
 
#Open averaged dark fits and plot.
hdulist = fits.open("final_dark.fit")
dark_data = hdulist[0].data
print dark_data
plt.imshow(dark_data)
plt.show()
plt.savefig("final_dark.png")
hdulist.close()
 
 
quit()
 
 
 
 
 
 
# 65535