# -*- coding: UTF-8 -*-
# cSpell:ignore astap NAXIS
import os
import tempfile
import subprocess

from astropy.io import fits
from astropy.wcs import WCS

from kcexo.data.fits import get_image_and_header, save_new_fits


def get_wcs(file_name: str, astap_exe: str = r"C:\Program Files\astap\astap_cli.exe") -> WCS:
    """Use ASTAP to get the WCS of the image.

    Args:
        file_name (str): Original image.
        astap_exe (str, optional): Location of the ASTAP CLI binary. Defaults to "C:\\Program Files\\astap\\astap_cli.exe".

    Returns:
        WCS: wcs for the image
    """
    header, data = get_image_and_header(file_name)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "tmp.fits")
        save_new_fits(header, data, path)
        subprocess.run([astap_exe, "-f", path, "-wcs", "-sip", "add", "y"], check=True)
    
        wcs_file = path.rsplit('.', maxsplit=1)[0]+".wcs"
        header = fits.Header.fromfile(path)
        wcs_fits_header = fits.Header.fromfile(wcs_file)
        if wcs_fits_header['NAXIS'] == 0:
            wcs_fits_header.set('NAXIS', 2, 'Number of axes')
            wcs_fits_header.insert('NAXIS', ('NAXIS1', header['NAXIS1'], header.comments['NAXIS1']), after=True)
            wcs_fits_header.insert('NAXIS', ('NAXIS2', header['NAXIS2'], header.comments['NAXIS2']), after=True)
    
    return WCS(wcs_fits_header), header


class FOV():
    """Abstraction of the field-of-view boundary polygon."""

    def __init__(self,
                 file_name: str,
                 wcs: WCS,
                 x_size: int,
                 y_size: int):
        self.file_name: str = file_name
        self.wcs: WCS = wcs
        self.x_size: int = x_size
        self.y_size: int = y_size
        
        self.c = wcs.pixel_to_world([0, 0, x_size, x_size, 0], [0, y_size, y_size, 0, 0])
        self.poly = [(e.ra.deg, e.dec.deg) for e in self.c]
    
    
    @staticmethod
    def from_image(file_name: str) -> "FOV":
        """Create FOV object from a file name.

        Args:
            file_name (str): name of the fits file to load.

        Returns:
            FOV: FOV object
        """
        header, _ = get_image_and_header(file_name)
        
        if "CTYPE1" not in header:
            wcs, header = get_wcs(file_name)
        else:
            wcs = WCS(header)

        x_size = header['NAXIS1']
        y_size = header['NAXIS2']
        
        return FOV(file_name, wcs, x_size, y_size)
