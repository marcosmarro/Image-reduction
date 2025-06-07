import glob
import numpy
import re
from matplotlib import pyplot as plt
from astropy.io import fits
from photometry import do_aperture_photometry
from photutils.centroids import centroid_sources


data_dir = '../../20250529/'


reduced_science_files = sorted(glob.glob(data_dir + "reduced_science*"), key=lambda x: int(re.search(r'reduced_science(\d+)', x).group(1)))


# After viewing the reduced file, the positions, radii, and annulus size are selected to perform aperture photometry
positions_1 = [(409, 403)]
positions_2 = [(485, 444)]
radii = [15]
sky_radius_in = 20
sky_annulus_width = 5


# Performs the aperture photometry given the information of the upper two comments
time_stamps = []
flux_data = []
all = []

for i in range(0, 143):
    science = fits.open(reduced_science_files[i])
    time_stamps.append(science[0].header['JD-OBS'])

    if i<121:
        tuple_array = centroid_sources(science[0].data.astype('f4'), xpos=positions_1[0][0], ypos=positions_1[0][1], box_size=15)
        position = [(round(tuple_array[0][0], 3),round(tuple_array[1][0], 3))]
        
    else:
        tuple_array = centroid_sources(science[0].data.astype('f4'), xpos=positions_2[0][0], ypos=positions_2[0][1], box_size=15)
        position = [(round(tuple_array[0][0], 3),round(tuple_array[1][0], 3))]

    all.append(position)   
    aperture_photometry_data = do_aperture_photometry(reduced_science_files[i],
    position,
    radii,
    sky_radius_in,
    sky_annulus_width,
    )

    flux_data.append(aperture_photometry_data[position[0]][1])


x_values = [float(point[0][0]) for point in all]
y_values = [float(point[0][1]) for point in all]
breakpoint()
plt.plot(time_stamps, flux_data)
plt.show()