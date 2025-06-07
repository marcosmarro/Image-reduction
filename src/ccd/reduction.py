#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Filename: reduction.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import pathlib
import numpy
import os
import pdb

def run_reduction(data_dir):
    """This function must run the entire CCD reduction process. You can implement it
    in any way that you want but it must perform a valid reduction for the two
    science frames in the dataset using the functions that you have implemented in
    this module. Then perform aperture photometry on at least one of the science
    frames, using apertures and sky annuli that make sense for the data.

    No specific output is required but make sure the function prints/saves all the
    relevant information to the screen or to a file, and that any plots are saved to
    PNG or PDF files.

    """
    
    import glob
    from bias import create_median_bias
    from darks import create_median_dark
    from flats import create_median_flat, plot_flat
    from photometry import do_aperture_photometry, plot_radial_profile
    from ptc import calculate_gain, calculate_readout_noise
    from science import reduce_science_frame


    current_dir = os.getcwd()
    print(current_dir)

    # Collects all the different types of images from the given directory, and sorts them in a list
    bias_files = sorted(glob.glob(data_dir + "Bias*"))
    dark_files = sorted(glob.glob(data_dir + "Dark*"))
    flat_files = sorted(glob.glob(data_dir + "domeflat*"))
    science_files = sorted(glob.glob(data_dir + "LPSEB*"))

    # Naming of the median filenames for the biases, darks, and flats
    median_bias_filename = data_dir + 'Median-Bias.fits'
    median_dark_filename = data_dir + 'Median-Dark.fits'
    median_flat_filename = data_dir + 'Median-AutoFlat.fits'

    breakpoint()
    # Creates the medians from the list of biases, darks, and flats
    median_bias = create_median_bias(bias_files, median_bias_filename)
    median_dark = create_median_dark(dark_files, median_bias_filename, median_dark_filename)
    median_flat = create_median_flat(flat_files, median_bias_filename, median_flat_filename, median_dark_filename)


    # Creates the plot for the median flat
    plot_flat(median_flat_filename, ouput_filename=data_dir + "median_flat.png", profile_ouput_filename=data_dir + "median_flat_profile.png")
    

    # Calculates and prints out the gain and readout noise from the list of flats and biases, respectively
    gain = calculate_gain(flat_files)
    print(f"Gain = {gain:.2f} e-/ADU")

    readout_noise = calculate_readout_noise(bias_files, gain)
    print(f"Readout Noise = {readout_noise:.2f} e-")


    # For loop to reduce each science image found in the list of science files, and save it with a reduced_science{i}.fits name
    for i in range(len(science_files)):
        science_filename = science_files[i]
        
        reduced_science = reduce_science_frame(
        science_filename,
        median_bias_filename,
        median_flat_filename,
        median_dark_filename,
        reduced_science_filename=f"{data_dir}reduced_science{i+1}.fits"
        )



    # Selects one of the reduced science files to perform aperture photometry    
    reduced_science_files = sorted(glob.glob(data_dir + "reduced_science*.fit*"))
    reduced_science_image = reduced_science_files[0]


    # After viewing the reduced file, the positions, radii, and annulus size are selected to perform aperture photometry
    positions = [(40, 331)]
    radii = numpy.linspace(.1, 30, 200)
    sky_radius_in = 35
    sky_annulus_width = 5

    
    # Performs the aperture photometry given the information of the upper two comments
    aperture_photometry_data = do_aperture_photometry(reduced_science_image,
    positions,
    radii,
    sky_radius_in,
    sky_annulus_width,
    )


    # Plots the radial profile after receiving the aperture photometry data
    plot_radial_profile(aperture_photometry_data, output_filename=data_dir + "radial_profile.png")
    
    
    return


data_dir = '../../20250529/'

run_reduction(data_dir)