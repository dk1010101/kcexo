# cSpell:ignore Teff logg
import copy
import astropy.units as u
from astropy.time import Time
from astropy.units import imperial
from astropy.coordinates import SkyCoord
from kcexo.star import Star
from kcexo.planet import ExoClockStatus, Planet

exo_status = {
    'priority': "HIGH",
    'min_aperture': 71.29,
    'min_aperture_t': 1 * imperial.inch,
    'ec_observations': 1,
    'ec_observations_recent': 0,
    'total_observations': 1,
    'total_observations_recent': 0,
    'oc': None,
}
star_mag = {
    'V': 5.96,
    'R': 5.4,
    'G': 5.714,
}
star = {
    "name": "rho01 Cnc",
    "c": SkyCoord("08:52:35.8113 +28:19:50.956", unit=(u.hourangle, u.deg)),
    "parallax": 79.427,
    "parallax_t": 1 * u.mas,
    "pm_ra": -485.872,
    "pm_ra_t": 1 * u.mas/u.year,
    "pm_dec": -233.651,
    "pm_dec_t": 1 * u.mas/u.year,
    "mag": star_mag,
    "Teff": 5234.0,
    "Teff_t": 1 * u.K,
    "Teff_e": 30.0,
    "Teff_e_t": 1 * u.K,
    "logg": 4.45,
    "logg_t": 1 * u.cm/u.s**2,
    "logg_e": 0.07,
    "logg_e_t": 1 * u.cm/u.s**2,
    "FeH": 0.31,
    "FeH_t": 1 * u.dex,
    "FeH_e": 0.04,
    "FeH_e_t": 1 * u.dex,
    "name_gaia": "DR2 704967037090946688",
    "name_2mass": "J08523579+2819509"
}
planet = {
    'name': "55Cnce",
    'ephem_mid_time': Time(2459340.807543, format='jd'),  # BJD, really
    'period': 0.73654625,
    'period_t': 1 * u.day,
    'RpRs': 0.0187,
    'aRs': 3.47,
    'i': 83.6,
    'i_t': 1 * u.deg,
    'depth': 0.45,
    'depth_t': 1 * u.mmag,
    'duration': 1.56,
    'duration_t': 1 * u.hour,
    'e': 0.0,
    'omega': 0.0,
    'omega_t': 1 * u.deg,
    'ephem_mid_time_e': 9.3E-5,
    'ephem_mid_time_e_t': 1 * u.day,
    'period_e': 1.5e-7,
    'period_e_t': 1 * u.day,
    'RpRs_e': 0.0004,
    'aRs_e': 0.07,
    'i_e': 0.6,
    'i_e_t': 1 * u.deg,
}

def test_full_creation():
    """simple create with full set of data"""
    
    exs = ExoClockStatus(
        priority = exo_status['priority'],
        min_aperture = exo_status['min_aperture'],
        ec_observations = exo_status['ec_observations'],
        ec_observations_recent = exo_status['ec_observations_recent'],
        total_observations = exo_status['total_observations'],
        total_observations_recent = exo_status['total_observations_recent'],
        oc = exo_status['oc']
    )
    s = Star(
        name = star["name"],
        c = star["c"],
        parallax = star["parallax"] * star["parallax_t"],
        pm_ra = star["pm_ra"] * star["pm_ra_t"],
        pm_dec = star["pm_dec"] * star["pm_dec_t"],
        mag = star["mag"],
        Teff = star["Teff"] * star["Teff_t"],
        Teff_e = star["Teff_e"] * star["Teff_e_t"],
        logg = star["logg"] * star["logg_t"],
        logg_e = star["logg_e"] * star["logg_e_t"],
        FeH = star["FeH"] * star["FeH_t"],
        FeH_e = star["FeH_e"] * star["FeH_e_t"],
        name_gaia = star["name_gaia"],
        name_2mass = star["name_2mass"]
    )
    p = Planet(
        name = planet['name'],
        host_star = s,
        ephem_mid_time = planet['ephem_mid_time'],
        period = planet['period'] * planet['period_t'],
        RpRs = planet['RpRs'],
        aRs = planet['aRs'],
        i = planet['i'] * planet['i_t'],
        depth = planet['depth'] * planet['depth_t'],
        duration = planet['duration'] * planet['duration_t'],
        e = planet['e'],
        omega = planet['omega'] * planet['omega_t'],
        ephem_mid_time_e = planet['ephem_mid_time_e'] * planet['ephem_mid_time_e_t'],
        period_e = planet['period_e'] * planet['period_e_t'],
        RpRs_e = planet['RpRs_e'],
        aRs_e = planet['aRs_e'],
        i_e = planet['i_e'] * planet['i_e_t'],
        status = exs
    )
    for key, value in planet.items():
        if '_t' in key:
            continue
        val = getattr(p, key)
        if key+'_t' not in planet.keys():  # pylint:disable=consider-iterating-dictionary
            assert val == value
        else:
            val_type = planet[key+"_t"]
            assert val.value == value
            assert val.unit == val_type.unit
    assert p.host_star == s
    assert p.status == exs
    
    # test equality
    assert p == p
    p2 = copy.deepcopy(p)
    p2.name = "foo"
    assert p != p2
