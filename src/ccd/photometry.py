#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Filename: photometry.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from astropy.io import fits
from astropy.stats import sigma_clip
import numpy
from photutils.aperture import CircularAnnulus, CircularAperture, aperture_photometry
from matplotlib import pyplot as plt

def do_aperture_photometry(
    image,
    positions,
    radii,
    sky_radius_in,
    sky_annulus_width,
):
    """This function must:

    - Accept a fully reduced science image as a file and read it.
    - Accept a list of positions on the image as a list of tuples (x, y).
    - Accept a list of aperture radii as a list of floats.
    - Accept a the radius at which to measure the sky background as sky_radius_in.
    - Accept a the width of the annulus as sky_annulus_width.
    - For each position and radius, calculate the flux in the aperture, subtracting
      the sky background. You can do this any way that you like but probably you'll
      want to use SkyCircularAnnulus from photutils.
    - The function should return the results from the aperture photometry. Usually
      this will be an astropy table from calling photutils aperture_photometry, but
      it can be something different if you use a different library.

    Note that the automated tests just check that you are returning from this
    function, but they do not check the contents of the returned data.

    """

    data = fits.getdata(image)
    results = dict()
    
    for position in positions:
        raw_fluxes = []
        fluxes = []
        for radius in radii:
            # Makes a circular aperture and caclulates the total flux in the area
            aperture = CircularAperture(position, radius)
            raw_flux = aperture_photometry(data, aperture)['aperture_sum'].value
            raw_fluxes.append(raw_flux[0])

            # Makes a circular annulus and calculates the total background flux in that area
            annulus = CircularAnnulus(position, sky_radius_in, sky_radius_in + sky_annulus_width)
            raw_background = aperture_photometry(data, annulus)['aperture_sum'].value

            # Grabs the background's mean in the annulus and multiplies it by aperture's area to grab background in only 
            # annulus
            background_mean = raw_background / annulus.area
            background = background_mean * aperture.area

            # Calculates total flux
            flux = raw_flux[0] - background[0]
            fluxes.append(flux)
            

        # Puts a dictionary where one position has a list of fluxes with change in radius
        results[position] = [radii, fluxes, raw_fluxes]

    
    return results


def plot_radial_profile(aperture_photometry_data, output_filename="radial_profile.png"):
    """This function must:

    - Accept a table of aperture photometry data as aperture_photometry_data. This
      is probably a photutils table, the result of do_aperture_photometry, but you
      can pass anything you like. The table/input data can contain a single target
      or multiple targets, but it must include multiple apertures.
    - Plot the radial profile of a target in the image using matplotlib. If you
      have multiple targets, label them correctly.
    - Plot a vertical line at the radius of the sky aperture used for the photometry.
    - Save the plot to the file specified in output_filename.

    """
    
    plt.figure()
    for key in aperture_photometry_data:
        position = key
        radii = numpy.array(aperture_photometry_data[key][0])
        fluxes = numpy.array(aperture_photometry_data[key][1])
        raw_fluxes = numpy.array(aperture_photometry_data[key][2])
        plt.plot(radii, fluxes / raw_fluxes)
        plt.xlabel('Radius')
        plt.ylabel('Normalized Flux')

    plt.title('Radial Profile of object(s)')
    plt.savefig(output_filename, dpi=500, bbox_inches='tight')

    return
