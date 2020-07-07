'''
Sean Keenan, 5th Year MPhys Heriot-Watt University, Edinburgh
Mazerra group
Gaussian Beam Profile Extraction
'''

# import relevant modules
import os
import numpy as np
import pandas as pd
from natsort import natsorted
from PIL import Image
import matplotlib.pyplot as mp
from scipy import optimize

# fit 1D gaussian to each matrix x-y dimension and extract parameters
# interpolate data to generate model of beam profile
# save and print data to excel sheet

''' Create functions to fit data '''

# define neccesary functions
def gauss_1d(height, centre, width):
    '''Generates Gaussian with given parameters'''
    return lambda x: height * np.exp(-(np.power(x - centre, 2) / (2 * width ** 2)))

# fit a gaussian to data by calculating its 'moments' (mean, variance, width, height)
def moments(data):
    '''Calculates parameters of a gaussian function by calculating its moments (height, centre, width_x, width_y'''
    height = np.amax(data)
    centre = np.where(data == height)
    mean_x = int(centre[0])
    mean_y = int(centre[1])
    row = data[mean_x, :]
    col = data[:, mean_y]
    width_x = np.sqrt(((row - height) ** 2).sum() / len(row))
    width_y = np.sqrt(((col - height) ** 2).sum() / len(col))
    return height, mean_x, width_x

def fitgauss_1d(data):
    '''Returns 2D Gaussian parameters from fit (height, x, width) '''
    params = moments(data)
    err_fun = lambda p: np.ravel(gauss_1d(*p)(*np.indices(data.shape)) - data)
    p, success = optimize.leastsq(err_fun, params)
    return p

''' Set-up Image file names and processing information '''

# directory name for images
path = '/Users/Message/Desktop/CCD data/20cm lens/'
file_list = os.listdir(path)
# extract relevant files and sort
image_list = natsorted([i for i in file_list if i.endswith('.bmp')])
xl_file = [i for i in file_list if i.endswith('.xls')]
# determine array dimensions for new data
img = Image.open(path + image_list[0])
imsize = img.size
# read image position (requires xlrd)
xlsx = pd.ExcelFile(path + xl_file[0])
z_pos = pd.read_excel(xlsx, sheet_name='Sheet1', header=2, usecols=['Distance (mm)'])

''' Read image and subtract background data - wont work if uneven number of files in folder '''

# read image and subtract background - store in new array
data = np.empty([int(len(image_list)/2), imsize[0], imsize[1]])
params = np.empty([int(len(image_list)/2), 5])
# fit = np.empty([int(len(image_list)/2), 5])
for index, image in enumerate(image_list):
    # break when half way through data
    if index < int(len(image_list)/2):
        # read then discard image (change to int32 as uint8 does not have -ve values)
        img = np.int32(np.transpose(np.asarray(Image.open(path + image_list[2 * index]))))
        bkd = np.int32(np.transpose(np.asarray(Image.open((path + image_list[2 * index + 1])))))
        # arrays of data, params and fit
        data[index, :, :] = np.absolute(img - bkd)
        params[index, :] = fitgauss_1d(data[index,:,:])
    else:
        break

mp.matshow(data[0,:], cmap=mp.cm.gist_earth_r)

fit = gauss_1d(*params[0,:])

mp.contour(fit(*np.indices(imsize)), cmap=mp.cm.copper)
ax = mp.gca()

print('finished')