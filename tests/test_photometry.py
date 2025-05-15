#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Filename: test_flats.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import pathlib

from astropy.io import fits
from photutils.datasets import load_star_image


def test_plot_radial_profile(tmp_path: pathlib.Path):
    """Tests plot_radial_profile()."""

    from ccd.photometry import do_aperture_photometry, plot_radial_profile

    data = load_star_image().data
    hdul = fits.HDUList([fits.PrimaryHDU(data=data)])
    hdul.writeto(str(tmp_path / "test_image.fits"), overwrite=True)

    apphot = do_aperture_photometry(
        str(tmp_path / "test_image.fits"),
        positions=[(100, 200)],
        radii=[10, 20, 30],
        sky_radius_in=40,
        sky_annulus_width=5,
    )

    assert apphot is not None, "Aperture photometry failed."

    plot_file = tmp_path / "test_radial_profile.png"
    plot_radial_profile(
        apphot,
        output_filename=str(plot_file),
    )

    assert plot_file.exists(), "Radial profile plot was not created."
