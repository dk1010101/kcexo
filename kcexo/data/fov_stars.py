# -*- coding: UTF-8 -*-
# cspell:ignore ICRS TICID otype vartyp oidref vmax vmin magtyp

from typing import NamedTuple, List

import numpy as np

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table
import pyvo as vo

from kcexo.fov import FOV


class MinMaxValue(NamedTuple):
    var_name: str
    min_value: float
    max_value: float
    allow_nan: bool


class FOVStars():
    
    def __init__(self,
                 fov: FOV,
                 target_name: str,
                 target_coordinates: SkyCoord,
                 limiting_mag: float = 16.0):
        self.fov: FOV = fov
        self.target_name: str = target_name
        self.target_coordinates: SkyCoord = target_coordinates
        self.limiting_mag: float = limiting_mag
        
        self.query: str
        self.table: Table
        
        self.create_query()
        self.get_stars()
    
    def create_query(self) -> None:
        """Create SIMBAD query for stars in the FOV."""
        polycoords = [item for row in self.fov.poly for item in row]
        self.query = f"""
SELECT DISTINCT
	   main_id AS "Object",
	   oid,
	   RA,
	   DEC,
	   otype,
	   mv.vartyp,
	   distance(POINT('ICRS', ra, dec),point('ICRS',{self.target_coordinates.ra.deg}, {self.target_coordinates.dec.deg})) as dist,
	   min(af.B)-min(af.V) as "B-V",
	   min(af.B) as "B", min(af.V) as "V", min(af.R) as "R",
	   i.id as "GaiaID",
	   i2.id as "TICID"
FROM basic b 
	 LEFT JOIN allfluxes af on af.oidref = oid
	 LEFT JOIN (
	   SELECT imv.epoch, imv.period, imv.vartyp, imv.vmax, imv.vmin, imv.magtyp, imv.oidref
	   FROM mesVar imv
	   WHERE imv.mespos = 1
	   ) as mv ON mv.oidref = oid
	 LEFT JOIN ident i on i.oidref = oid AND i.id LIKE 'Gaia DR2%'
	 LEFT JOIN ident i2 on i2.oidref = oid AND i2.id LIKE 'TIC %' 
WHERE 
  otype = '*..'
  AND ((af.B IS NOT NULL and af.B < {self.limiting_mag}) OR (af.V IS NOT NULL and af.V < {self.limiting_mag}) OR (af.R IS NOT NULL and af.R < {self.limiting_mag}))
  AND CONTAINS(POINT('ICRS', RA, DEC), POLYGON('ICRS', {','.join(map(str, polycoords))})) = 1
GROUP BY main_id, oid, RA, DEC, otype, mv.vartyp, mv.epoch, mv.period, mv.magtyp, mv.vmin, mv.vmax, mv.oidref, af.oidref,i.id, i2.id
ORDER BY dist, "B-V", RA, DEC
"""

    
    def get_stars(self) -> None:
        """Get all stars in the FOV."""
        simbad = vo.dal.TAPService("https://simbad.cds.unistra.fr/simbad/sim-tap")
        simjob = simbad.submit_job(self.query)
        simjob.run()
        simjob.wait()
        self.table = simjob.fetch_result().to_table()

    def filter_stars(self, filter_spec: List[MinMaxValue]) -> Table:
        """Give a list of min-max filter specifications, return the table with the matching data.

        Args:
            filter_spec (List[MinMaxValue]): List of min-max filter specifications.

        Returns:
            Table: table with the matching data
        """
        fvs = [True] * len(self.table)
        main_star = self.table['dist'] == 0.0
        all_f = [False] * len(self.table)
        for f in filter_spec:
            f1 = self.table[f.var_name] >= f.min_value
            f2 = self.table[f.var_name] <= f.max_value
            if f.allow_nan:
                f3 = np.isnan(self.table[f.var_name])
            else:
                f3 = all_f
            fvs = fvs & ((f1 & f2) | f3)
        return self.table[main_star | fvs]
