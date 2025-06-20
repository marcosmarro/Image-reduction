import glob
import numpy
import re
from astropy.io import fits
from photometry import do_aperture_photometry
from photutils.centroids import centroid_sources, centroid_quadratic


# Grabs all science files and sorts them numerically
data_dir = '../../20250529/'
reduced_science_files = sorted(glob.glob(data_dir + "reduced_science*"), key=lambda x: int(re.search(r'reduced_science(\d+)', x).group(1)))


# After viewing the reduced file, the radii, annulus size, and positions are selected to perform aperture photometry
radii = [10]
sky_radius_in = 18
sky_annulus_width = 4


# x and y poistions of both target and comparison objects, where first entry is target and last two are comparison
x_positions_1 = numpy.array([409, 387, 570]) # 1st set is a rough estimate of position for first 121 files
y_positions_1 = numpy.array([408, 520, 107])

x_positions_2 = numpy.array([485, 463, 645]) # 2nd set is a rough estimate of position for last 22 files since camera didn't center
y_positions_2 = numpy.array([444, 560, 148])


# Creates empty lists of the time stamps, target flux, and comparison fluxes
time_stamps = []
target_flux = []
comparison_flux = []


# Performs the aperture photometry given the information of the upper two comments
for i in range(len(reduced_science_files)):
    science = fits.open(reduced_science_files[i])
    time_stamps.append(science[0].header['JD-OBS'])
    data = science[0].data.astype('f4') 

    # Accurately finds the position of each object (target + 2 comparisons) 
    # Creates a list of positions as a list of tuples for the 3 objects to later perform aperture photometry
    if i<121:
        tuple_array = centroid_sources(data - numpy.median(data), xpos=x_positions_1, ypos=y_positions_1, box_size=35, centroid_func=centroid_quadratic)
        position = list(zip(tuple_array[0], tuple_array[1]))
        
    else:
        tuple_array = centroid_sources(data - numpy.median(data), xpos=x_positions_2, ypos=y_positions_2, box_size=35, centroid_func=centroid_quadratic)
        position = list(zip(tuple_array[0], tuple_array[1]))

    # Performs aperture photometry and returns a dictionary in the format:
    # {(x, y): [radii, fluxes, raw_fluxes]}, in this case will return a dictionary with 3 keys (the 3 different positions)
    aperture_photometry_data = do_aperture_photometry(reduced_science_files[i], position, radii, sky_radius_in, sky_annulus_width)
    
    # Appends flux of target and mean of two comparison objects to their respective lists
    target_flux.append(aperture_photometry_data[position[0]][1][0])
    comparison_flux.append(1/2 * (aperture_photometry_data[position[1]][1][0] + aperture_photometry_data[position[2]][1][0])) 


ratio = numpy.array(target_flux) / numpy.array(comparison_flux)
time = (numpy.array(time_stamps) - numpy.min(time_stamps)) * 24 * 60  # Sets time to minutes after first observation

numpy.save("times.npy", time)
numpy.save("fluxes.npy", ratio)