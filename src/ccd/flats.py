#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Filename: flats.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from astropy.io import fits
from astropy.stats import sigma_clip
import numpy
from astropy.visualization import ImageNormalize, LinearStretch, ZScaleInterval
from matplotlib import pyplot as plt

def create_median_flat(
    flat_list,
    bias_filename,
    median_flat_filename,
    dark_filename=None,
):
    """This function must:

    - Accept a list of flat file paths to combine as flat_list. Make sure all
      the flats are for the same filter.
    - Accept a median bias frame filename as bias_filename (the one you created using
      create_median_bias).
    - Read all the images in flat_list and create a list of 2D numpy arrays.
    - Read the bias frame.
    - Subtract the bias frame from each flat image.
    - Optionally you can pass a dark frame filename as dark_filename and subtract
      the dark frame from each flat image (remember to scale the dark frame by the
      exposure time of the flat frame).
    - Use a sigma clipping algorithm to combine all the bias-corrected flat frames
      using the median and removing outliers outside 3-sigma for each pixel.
    - Create a normalised flat divided by the median flat value.
    - Save the resulting median flat frame to a FITS file with the name
      median_flat_filename.
    - Return the normalised median flat frame as a 2D numpy array.

    """

    bias = fits.getdata(bias_filename)
    flat_bias_data = []

    # Will read each file and append to dark_bias_data list where the arrays have dtype = float32
    for file in flat_list:
        flat = fits.open(file)
        flat_data = flat[0].data[1536:2560, 1536:2560].astype('f4')

        # Subtracts bias from each flat and adds to flat_bias_data list
        flat_bias_data.append(flat_data - bias) 

    # Reads the list of flats and sigma clips the arrays
    flat_sc = sigma_clip(flat_bias_data, cenfunc='median', sigma=3, axis=0)

    # Creates a final 2D array that is the mean of each pixel from all different flats, and then divides by the median 
    # flat value to normalize
    flat = numpy.ma.mean(flat_sc, axis=0)

    # Normalizes the resulting flat to get the median flat
    median_flat = flat / numpy.median(flat)

    # Create a new FITS file from the resulting median dark frame.
    flat_hdu = fits.PrimaryHDU(data=median_flat.data, header=fits.Header())
    flat_hdu.header['COMMENT'] = 'Normalized flat image with bias subtracted'
    hdul = fits.HDUList([flat_hdu])
    hdul.writeto(median_flat_filename, overwrite=True)

    return median_flat


def plot_flat(
    median_flat_filename,
    ouput_filename="median_flat.png",
    profile_ouput_filename="median_flat_profile.png",
):
    """This function must:

    - Accept a normalised flat file path as median_flat_filename.
    - Read the flat file.
    - Plot the flat frame using matplotlib.imshow with reasonable vmin and vmax
      limits. Save the plot to the file specified by output_filename.
    - Take the median of the flat frame along the y-axis. You'll end up with a
      1D array.
    - Plot the 1D array using matplotlib.
    - Save the plot to the file specified by profile_output_filename.

    """

    # Reads the normalized flat file
    flat = fits.open(median_flat_filename)
    flat_data = flat[0].data.astype('f4')

    # Plots and saves the flat frame using imshow
    plt.figure()
    norm = ImageNormalize(flat_data, interval=ZScaleInterval(), stretch=LinearStretch())
    flat_frame = plt.imshow(flat_data, origin='lower', norm=norm, cmap='YlOrBr_r')
    plt.savefig(ouput_filename, dpi=500, bbox_inches='tight')
    plt.close()

    # Plots and saves the flat median fame
    plt.figure()
    flat_profile = numpy.median(flat_data, axis=0)
    median_flat_profile = plt.plot(flat_profile)
    plt.savefig(profile_ouput_filename, dpi=500, bbox_inches='tight')
    plt.close()

    return
