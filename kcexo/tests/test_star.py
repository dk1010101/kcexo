# -*- coding: UTF-8 -*-
# cSpell:ignore Teff logg
# pylint:disable=missing-function-docstring
import copy
import astropy.units as u
from astropy.coordinates import SkyCoord

from kcexo.star import Star

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



def test_full_creation():
    """simple create with full set of data"""
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
    for key, value in star.items():
        if '_t' in key:
            continue
        val = getattr(s, key)
        if key+'_t' not in star.keys():  # pylint:disable=consider-iterating-dictionary
            assert val == value
        else:
            val_type = star[key+"_t"]
            assert val.value == value
            assert val.unit == val_type.unit

    assert s.name == s.name_simbad
    assert s == s
    s2 = copy.deepcopy(s)
    s2.name = "foo"
    assert s != s2

def test_creation_no_e():
    """simple create with full set of data"""
    s = Star(
        name = star["name"],
        c = star["c"],
        parallax = star["parallax"] * star["parallax_t"],
        pm_ra = star["pm_ra"] * star["pm_ra_t"],
        pm_dec = star["pm_dec"] * star["pm_dec_t"],
        mag = star["mag"],
        Teff = star["Teff"] * star["Teff_t"],
        logg = star["logg"] * star["logg_t"],
        FeH = star["FeH"] * star["FeH_t"],
        name_gaia = star["name_gaia"],
        name_2mass = star["name_2mass"]
    )
    for key, value in star.items():
        if '_t' in key:
            continue
        val = getattr(s, key)
        if key+'_t' not in star.keys():  # pylint:disable=consider-iterating-dictionary
            assert val == value
        else:
            val_type = star[key+"_t"]
            if '_e' in key:
                assert val.value == 0.0
            else:
                assert val.value == value
            assert val.unit == val_type.unit
    assert s == s
    s2 = copy.deepcopy(s)
    s2.name = "foo"
    assert s != s2


def test_equality_exoclock():
    s1 = Star(
        name = star["name"],
        c = star["c"],
        parallax = star["parallax"] * star["parallax_t"],
        pm_ra = star["pm_ra"] * star["pm_ra_t"],
        pm_dec = star["pm_dec"] * star["pm_dec_t"],
        mag = star["mag"],
        Teff = star["Teff"] * star["Teff_t"],
        logg = star["logg"] * star["logg_t"],
        FeH = star["FeH"] * star["FeH_t"],
        name_gaia = star["name_gaia"],
        name_2mass = star["name_2mass"]
    )
    s2 = copy.deepcopy(s1)
    s2.parallax *= -1.0
    s2.pm_dec *= -1.0
    s2.pm_ra *= -1.0
    s2.name_gaia = "no name"
    s2.name_2mass = "no name"
    
    s1.EQ_EXOCLOCK_ONLY = True
    s2.EQ_EXOCLOCK_ONLY = True
    assert s1 == s2
    assert s2 == s1
    
def test_equality_no_exoclock():
    s1 = Star(
        name = star["name"],
        c = star["c"],
        parallax = star["parallax"] * star["parallax_t"],
        pm_ra = star["pm_ra"] * star["pm_ra_t"],
        pm_dec = star["pm_dec"] * star["pm_dec_t"],
        mag = star["mag"],
        Teff = star["Teff"] * star["Teff_t"],
        logg = star["logg"] * star["logg_t"],
        FeH = star["FeH"] * star["FeH_t"],
        name_gaia = star["name_gaia"],
        name_2mass = star["name_2mass"]
    )
    s2 = copy.deepcopy(s1)
    s2.parallax *= -1.0
    s2.pm_dec *= -1.0
    s2.pm_ra *= -1.0
    s2.name_gaia = "no name"
    s2.name_2mass = "no name"
    
    s1.EQ_EXOCLOCK_ONLY = False
    assert s1 != s2

    # but now we don't have associative equality!
    assert s2 == s1

    # and now we do but it is not automatic!
    s2.EQ_EXOCLOCK_ONLY = False
    assert s2 != s1
