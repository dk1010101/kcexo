# -*- coding: UTF-8 -*-
# cSpell:ignore exoclock isot astropy
import itertools
import json
import urllib
from pathlib import Path
from io import StringIO

import astropy.units as u
from astropy.time import Time
from astropy.table import Table
from astropy.coordinates import EarthLocation

from kcexo.source.source import Source, fix_str_types


class ExoClock(Source):
    """Wrapper around Exoclock datasource"""
    name = 'exoclock'
    
    def __init__(self, 
                 file_root: Path,
                 file_stem_override: str = "",
                 max_age: u.Quantity["time"] = 1 * u.day):
        """Initialise the object. All the work is done by the parent class."""
        super().__init__(file_root, file_stem_override, max_age)
        
    def _load_data_from_remote(self) -> None:
        """Load data from the online source."""
        self.log.info("Fetching the new set of exoclock data from www.exoclock.space")
        js_str = urllib.request.urlopen('https://www.exoclock.space/database/planets_json').read().decode()
        sio = StringIO(js_str)
        js = json.load(sio)
        common_keys = list(dict.fromkeys(itertools.chain.from_iterable(list(map(lambda c: list(c.keys()), js.values())))))
        v = {k: [dic.get(k, '') for dic in js.values()] for k in common_keys}
        exoplanets_data = Table(v, names=common_keys)
        fix_str_types(exoplanets_data)
        self.data['data'] = exoplanets_data

def exoclock_to_u(exo_unit: str) -> u.Unit|float:
    """Convert exoclock unit in to an `astropy` unit"""
    if exo_unit == "Days":
        return u.day
    elif exo_unit == "Hours":
        return u.hour
    elif exo_unit == "Seconds":
        return u.second
    elif exo_unit == "Degrees":
        return u.deg
    elif exo_unit == "Radians":
        return u.rad
    elif exo_unit == "Kelvin":
        return u.K
    elif exo_unit == "cm/s2":
        return u.cm / u.s**2
    elif exo_unit[:3] == "dex":
        return u.dex
    elif exo_unit == "None":
        return 1.0
    else:
        raise ValueError(f"Unsupported unit: {exo_unit}")
    
def exoclock_t_t(time_string: str, time_fmt: str, location: EarthLocation|None = None) -> Time:
    """Convert exoclock time in to `astropy` time"""
    fmt, scale = time_fmt.split("_")
    if fmt == "BJD" or fmt == "JD":
        f = "jd"
    elif fmt == "MJD":
        f = "mjd"
    else:
        raise ValueError(f"Unknown time format: {fmt}")
    s = scale.lower()
    if s == 'local':
        s = 'Local'
    return Time(time_string, format=f, scale=s, location=location)
