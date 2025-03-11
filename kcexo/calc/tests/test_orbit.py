# -*- coding: UTF-8 -*-
# cSpell:ignore Teff logg
# pylint:disable=missing-function-docstring
import numpy as np
import pytest
import astropy.units as u

from kcexo.calc.orbits import transit_duration, transit_t12


stars = [
    # name, inputs (Rp/Rs, a/Rs, period, e, i, ww), expected ((duration, error), (t12, error))
    ('HD 80606', # from 2009ApJ...703.2091W "The Transit Ingress and the Tilted Orbit of the Extraordinarily Eccentric Exoplanet HD 80606b"
     (
        0.1033,
        102.4,
        111.43740 * u.day,
        0.93286,
        89.324 * u.deg,
        300.83 * u.deg
     ), 
     (
        (2.60 * u.hour, 0.18 * u.hour),
        (11.64 * u.hour, 0.25 * u.hour)
     )
    ),
    ('HD 149026', # from 2009PhDT.......365C "Analysis of exoplanetary transit light curves"
     (
        0.05416,
        6.01,
        2.8758916 * u.day,
        0.013,
        84.55 * u.deg,
        0.0 * u.deg
     ), 
     (
        (0.241 * u.hour, 0.012 * u.hour),
        (3.24 * u.hour, 0.15 * u.hour)
     )
    ),
]


@pytest.mark.parametrize("name, inputs, expected", stars)
def test_duration_t12(name, inputs, expected) -> None:  # pylint:disable=unused-argument
    rp_over_rs = inputs[0]
    sma_over_rs = inputs[1]
    period = inputs[2]
    eccentricity = inputs[3]
    inclination = inputs[4]
    periastron = inputs[5]
    
    exp_t12 = expected[0][0]
    exp_t12_e = expected[0][1]
    exp_duration = expected[1][0]
    exp_duration_e = expected[1][1]
    
    duration = transit_duration(rp_over_rs, period, sma_over_rs, eccentricity, inclination, periastron)
    t12 = transit_t12(rp_over_rs, period, sma_over_rs, eccentricity, inclination, periastron)
    
    assert np.abs(duration - exp_duration) <= exp_duration_e
    assert np.abs(t12 - exp_t12) <= exp_t12_e
