import numpy as np
import astropy.units as u
from astropy.time import Time


def equal_times(t1: Time, 
                  t2: Time, 
                  delta: u.Quantity["time"]) -> bool:
    """Compare two times up to some time delta"""
    return np.abs((t1 - t2).to(u.s).value) < delta.to(u.s).value
