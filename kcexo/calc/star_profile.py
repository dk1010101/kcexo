
import numpy as np

from photutils.detection import DAOStarFinder
from photutils.psf import (CircularGaussianPRF, fit_fwhm,

                           make_psf_model_image)

def calc_fwhms(image: np.ndarray) -> np.ndarray:
    