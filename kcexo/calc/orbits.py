# -*- coding: UTF-8 -*-
# cSpell:ignore Angelos Tsiaras
import warnings
import numpy as np
import astropy.units as u
from scipy.optimize import curve_fit as scipy_curve_fit


# These functions have been copied from Angelos Tsiaras' HOPS `exoplanet_lc.py` file and then modified with types and Quantities.




def curve_fit(*args, **kwargs) -> tuple:
    """Fit a curve"""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",
                                message='Covariance of the parameters could not be estimated')
        return scipy_curve_fit(*args, **kwargs)


def planet_orbit(period_in: u.Quantity['time'], 
                 sma_over_rs: float, 
                 eccentricity: float, 
                 inclination_in: u.Quantity['angle'], 
                 periastron_in: u.Quantity['angle'],
                 mid_time: float, 
                 time_array: list, 
                 ww_in: u.Quantity['angle'] = 0 * u.rad) -> tuple:
    """Calculate the orbit in XYZ for a planet"""
    inclination = inclination_in.to(u.rad).value
    periastron = periastron_in.to(u.rad).value
    period = period_in.to(u.day).value
    ww = ww_in.to(u.rad).value
    
    if eccentricity == 0 and ww == 0:

        e_t = (2 * np.pi / period) * (time_array - mid_time)
        cos_e_t = np.cos(e_t)
        sin_e_t = np.sin(e_t)

        x_t = (sma_over_rs * np.sin(inclination)) * cos_e_t
        y_t = sma_over_rs * sin_e_t
        z_t = (- sma_over_rs * np.cos(inclination)) * cos_e_t

    else:

        f_tmid = np.pi / 2 - periastron
        e_tmid = 2 * np.arctan(np.sqrt((1 - eccentricity) / (1 + eccentricity)) * np.tan(f_tmid / 2))
        if e_tmid < 0:
            e_tmid += 2 * np.pi
        tp = mid_time - (period / 2.0 / np.pi) * (e_tmid - eccentricity * np.sin(e_tmid))

        m = (time_array - tp - np.int_((time_array - tp) / period) * period) * 2.0 * np.pi / period
        e_t0 = m
        e_t = e_t0
        stop = False
        for _ in range(10000):  # setting a limit of 10k iterations - arbitrary limit
            e_t = e_t0 - (e_t0 - eccentricity * np.sin(e_t0) - m) / (1 - eccentricity * np.cos(e_t0))
            stop = (np.abs(e_t - e_t0) < 10 ** (-7)).all()
            if stop:
                break
            else:
                e_t0 = e_t
        if not stop:
            raise RuntimeError('Failed to find a solution in 10000 loops')

        f_t = 2 * np.arctan(np.sqrt((1 + eccentricity) / (1 - eccentricity)) * np.tan(e_t / 2))
        r_t = sma_over_rs * (1 - (eccentricity ** 2)) / (1 + eccentricity * np.cos(f_t))
        f_t_plus_periastron = f_t + periastron
        cos_f_t_plus_periastron = np.cos(f_t_plus_periastron)
        sin_f_t_plus_periastron = np.sin(f_t_plus_periastron)

        x_t = r_t * sin_f_t_plus_periastron * np.sin(inclination)

        if ww == 0:
            y_t = - r_t * cos_f_t_plus_periastron
            z_t = - r_t * sin_f_t_plus_periastron * np.cos(inclination)

        else:
            y_t = - r_t * (cos_f_t_plus_periastron * np.cos(ww) - sin_f_t_plus_periastron * np.sin(ww) * np.cos(inclination))
            z_t = - r_t * (cos_f_t_plus_periastron * np.sin(ww) + sin_f_t_plus_periastron * np.cos(ww) * np.cos(inclination))

    return [x_t, y_t, z_t]


def planet_star_projected_distance(period: u.Quantity['time'], 
                                   sma_over_rs: float, 
                                   eccentricity: float, 
                                   inclination: u.Quantity['angle'], 
                                   periastron: u.Quantity['angle'],
                                   mid_time: float, 
                                   time_array: list) -> float:
    """Calculate the projected distance between the star and the planet"""
    _, y_t, z_t = planet_orbit(period, sma_over_rs, eccentricity, inclination, periastron, mid_time, time_array)

    return np.sqrt(y_t * y_t + z_t * z_t)

def transit_duration(rp_over_rs: float, 
                     period_in: u.Quantity['time'], 
                     sma_over_rs: float, 
                     eccentricity: float, 
                     inclination_in: u.Quantity['angle'], 
                     periastron_in: u.Quantity['angle']) -> u.Quantity['time']:
    """Total transit duration calculated using function solving"""
    ww = periastron_in.to(u.rad).value
    ii = inclination_in.to(u.rad).value
    period = period_in.to(u.day).value
    ee = eccentricity
    aa = sma_over_rs
    ro_pt = (1 - ee ** 2) / (1 + ee * np.sin(ww))
    b_pt = aa * ro_pt * np.cos(ii)
    if b_pt > 1:
        b_pt = 0.5
    s_ps = 1.0 + rp_over_rs
    df = np.arcsin(np.sqrt((s_ps ** 2 - b_pt ** 2) / ((aa ** 2) * (ro_pt ** 2) - b_pt ** 2)))
    aprox = (period * (ro_pt ** 2)) / (np.pi * np.sqrt(1 - ee ** 2)) * df * 60 * 60 * 24

    def function_to_fit(_, t):
        return planet_star_projected_distance(period_in, sma_over_rs, eccentricity, inclination_in, periastron_in,
                                              10000, np.array(10000 + t / 24 / 60 / 60))

    popt1, _ = curve_fit(function_to_fit, [0], [1.0 + rp_over_rs], p0=[-aprox / 2])  # pylint:disable=unbalanced-tuple-unpacking
    popt2, _ = curve_fit(function_to_fit, [0], [1.0 + rp_over_rs], p0=[aprox / 2])  # pylint:disable=unbalanced-tuple-unpacking

    return (popt2[0] - popt1[0]) * u.s


def transit_t12(rp_over_rs: float, 
                period: u.Quantity['time'], 
                sma_over_rs: float, 
                eccentricity: float, 
                inclination: u.Quantity['angle'], 
                periastron: u.Quantity['angle']) -> u.Quantity['time']:
    """Transit T12 calculated using function solving"""
    aprox = transit_duration(rp_over_rs, period, sma_over_rs, eccentricity, inclination, periastron).to(u.s).value

    def function_to_fit(_, t):
        return planet_star_projected_distance(period, sma_over_rs, eccentricity, inclination, periastron,
                                              10000, np.array(10000 + t / 24 / 60 / 60))

    popt1, _ = curve_fit(function_to_fit, [0], [1.0 + rp_over_rs], p0=[-aprox / 2])  # pylint:disable=unbalanced-tuple-unpacking
    popt2, _ = curve_fit(function_to_fit, [0], [1.0 - rp_over_rs], p0=[-aprox / 2])  # pylint:disable=unbalanced-tuple-unpacking

    res = min(
        (popt2[0] - popt1[0]) / 24 / 60 / 60,
        0.5*transit_duration(rp_over_rs, period, sma_over_rs, eccentricity, inclination, periastron).to(u.day).value
        ) 
    return res * u.day
