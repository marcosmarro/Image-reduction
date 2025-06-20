#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Filename: reduction.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


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
    from flats import create_median_flat
    from ptc import calculate_gain, calculate_readout_noise
    from science import reduce_science_frame


    # Collects all the different types of images from the given directory, and sorts them in a list
    bias_files = sorted(glob.glob(data_dir + "Bias*"))
    dark_files = sorted(glob.glob(data_dir + "Dark*"))
    flat_files = sorted(glob.glob(data_dir + "domeflat*"))
    science_files = sorted(glob.glob(data_dir + "LPSEB*"))

    # Naming of the median filenames for the biases, darks, and flats
    median_bias_filename = data_dir + 'Median-Bias.fits'
    median_dark_filename = data_dir + 'Median-Dark.fits'
    median_flat_filename = data_dir + 'Median-AutoFlat.fits'

    
    # Creates the medians from the list of biases, darks, and flats
    median_bias = create_median_bias(bias_files, median_bias_filename)
    median_dark = create_median_dark(dark_files, median_bias_filename, median_dark_filename)
    median_flat = create_median_flat(flat_files, median_bias_filename, median_flat_filename, median_dark_filename)
    

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

    
    return


data_dir = '../../20250529/'

run_reduction(data_dir)