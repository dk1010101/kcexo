# -*- coding: UTF-8 -*-
# cSpell:ignore ndarray
from pathlib import Path
from typing import Tuple

import numpy as np

from astropy.io import fits


def get_image_and_header(fname: str|Path, image_hdu_index: int=0) -> Tuple[fits.Header, np.ndarray]:
    """Open a fits file and get the image and the header even if it is compressed etc.
    
    Args:
        fname (str|Path): FITS file name. Could the compressed or vanilla.
        image_hdu_index (int, optional): Which image HDU to get counting in sequential order? Default is 0 meaning "first".

    Returns:
        Tuple[fits.Header, fits.ImageHDU]: The FITS image header and the data.
    """
    p = fname
    if isinstance(fname, str):
        p = Path(fname)
        
    data = None
    header = None
    idx_pos = 0
    
    hdu = fits.open(p.as_posix(), decompress_in_memory=True)
    for hd in hdu:
        header = hd.header
        if isinstance(hd, fits.PrimaryHDU):
            if ('EXPTIME' in header or 'EXPOSURE' in header) and 'FILTER' in header:
                # this is probably an image...
                if idx_pos == image_hdu_index:
                    data = hd.data
                    break
                else:
                    idx_pos += 1
        elif isinstance(hd, fits.ImageHDU):
            if idx_pos == image_hdu_index:
                data = hd.data
                break
            else:
                idx_pos += 1
        elif isinstance(hd, fits.CompImageHDU):
            if idx_pos == image_hdu_index:
                data = hd.data
                break
            else:
                idx_pos += 1

    return (header, data)


def save_new_fits(header: fits.Header, data: np.ndarray, new_file_name: str) -> None:
    """Create a new FITS file from a header and some data.

    Existing files will be replaced.

    Args:
        header (fits.Header): Valid FITS header
        data (np.ndarray): valid data array
        new_file_name (str): Name of the new file.
    """
    hdu = fits.PrimaryHDU(data, header)
    hdu.writeto(new_file_name, overwrite=True)
        