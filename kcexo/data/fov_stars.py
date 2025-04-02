# -*- coding: UTF-8 -*-
# cspell:ignore ICRS TICID otype vartyp oidref vmax vmin magtyp phot gaiadr
from dataclasses import dataclass
from typing import List, Any

import numpy as np

from astropy.coordinates import SkyCoord
from astropy.table import Table
import pyvo as vo
from astroquery.gaia import Gaia

from kcexo.fov import FOV


@dataclass
class GenericFilter():
    """Base class for all filters. Needed so that we can use it as a placeholder"""


@dataclass
class FilterMinMaxValue(GenericFilter):
    """Filter by min/max values and optionally allow NaNs"""
    var_name: str
    min_value: float
    max_value: float
    allow_nan: bool


@dataclass
class FilterNotValue(GenericFilter):
    """Filter by checking that something is not of a particular value and optionally allow NaNs"""
    var_name: str
    not_value: Any
    allow_nan: bool
    

@dataclass
class FilterIsValue(GenericFilter):
    """Filter by checking that something is of a particular value and optionally allow NaNs"""
    var_name: str
    value: Any
    allow_nan: bool

    
@dataclass
class FilterOrIsValue(GenericFilter):
    """Filter by checking that something is of a particular value as well as something else (see implementation)"""
    var_name: str
    value: Any
    

class FOVStars():
    """All the stars in a particular FOV"""
    def __init__(self,
                 fov: FOV,
                 target_name: str,
                 target_coordinates: SkyCoord,
                 limiting_mag: float = 16.0):
        self.fov: FOV = fov
        self.target_name: str = target_name
        self.target_coordinates: SkyCoord = target_coordinates
        self.limiting_mag: float = limiting_mag
        
        self.simbad_query: str
        self.simbad_table: Table
        
        self.gaia_query_by_name: str
        self.gaia_query: str
        self.gaia_by_name: Table
        self.gaia_by_fov: Table
        
        self.get_stars()
    
    def create_simbad_query(self) -> None:
        """Create SIMBAD query for stars in the FOV."""
        polycoords = [item for row in self.fov.poly for item in row]
        self.simbad_query = f"""
SELECT DISTINCT
	   main_id AS "Object",
	   oid,
	   RA,
	   DEC,
	   otype,
	   mv.vartyp as "vartyp",
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
	 LEFT JOIN ident i on i.oidref = oid AND i.id LIKE 'Gaia DR3%'
	 LEFT JOIN ident i2 on i2.oidref = oid AND i2.id LIKE 'TIC %' 
WHERE 
  otype = '*..'
  AND (
       (
        (
            (af.B IS NOT NULL and af.B <= {self.limiting_mag}) 
            OR (af.V IS NOT NULL and af.V <= {self.limiting_mag}) 
            OR (af.R IS NOT NULL and af.R <= {self.limiting_mag})
        )
        AND CONTAINS(POINT('ICRS', RA, DEC), POLYGON('ICRS', {','.join(map(str, polycoords))})) = 1
       )
       OR (
           CONTAINS(POINT('ICRS', RA, DEC), CIRCLE('ICRS', {self.target_coordinates.ra.deg}, {self.target_coordinates.dec.deg}, 0.0001)) = 1
          )
      )
GROUP BY main_id, oid, RA, DEC, otype, mv.vartyp, mv.epoch, mv.period, mv.magtyp, mv.vmin, mv.vmax, mv.oidref, af.oidref,i.id, i2.id
ORDER BY dist, "B-V", RA, DEC
"""
        # print(self.simbad_query)

    def create_gaia_query_by_name(self) -> None:
        """Get all gaia star details by gaia id"""
        names = self.simbad_table['GaiaID']
        self.gaia_query_by_name = f"""
SELECT DISTINCT
    source_id,
    designation,
    ref_epoch,
    ra,
    dec,
    distance(POINT('ICRS', ra, dec),point('ICRS',{self.target_coordinates.ra.deg}, {self.target_coordinates.dec.deg})) as dist,
	phot_bp_mean_mag-phot_rp_mean_mag as "Gbp-Grp",
    phot_g_mean_mag as "G", 
    phot_bp_mean_mag as "Gbp", 
    phot_rp_mean_mag as "Grp"
FROM gaiadr3.gaia_source
WHERE designation IN ('{"','".join(names.astype(str))}')
"""

    def create_gaia_query_fov(self) -> None:
        """Create a query to get Gaia stars"""
        names = self.simbad_table['GaiaID']
        polycoords = [item for row in self.fov.poly for item in row]
        self.gaia_query = f"""
SELECT DISTINCT
    source_id,
    designation,
    ref_epoch,
    ra,
    dec,
    distance(POINT('ICRS', ra, dec),point('ICRS',{self.target_coordinates.ra.deg}, {self.target_coordinates.dec.deg})) as dist,
	phot_bp_mean_mag-phot_rp_mean_mag as "Gbp-Grp",
    phot_g_mean_mag as "G", 
    phot_bp_mean_mag as "Gbp", 
    phot_rp_mean_mag as "Grp"
FROM gaiadr3.gaia_source
WHERE 
    CONTAINS(POINT('ICRS', RA, DEC), POLYGON('ICRS', {','.join(map(str, polycoords))})) = 1
    AND phot_g_mean_mag <= {self.limiting_mag}
    AND designation NOT IN ('{"','".join(names.astype(str))}')
ORDER BY source_id
"""

    def get_stars(self) -> None:
        """Get all stars in the FOV."""
       
        # SIMBAD 
        self.create_simbad_query()
        simbad = vo.dal.TAPService("https://simbad.cds.unistra.fr/simbad/sim-tap")
        simjob = simbad.submit_job(self.simbad_query)
        simjob.run()
        simjob.wait()
        self.simbad_table = simjob.fetch_result().to_table()
        
        # GAIA
        self.create_gaia_query_by_name()
        # self.create_gaia_query_fov()
        Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
        job = Gaia.launch_job_async(self.gaia_query_by_name)
        self.gaia_by_name = job.get_results()
        # job = Gaia.launch_job_async(self.create_gaia_query_fov)
        # self.gaia_by_fov = job.get_results()
        
        # populate simbad with gaia columns
        num_rows = len(self.simbad_table['GaiaID'])
                
        col = [np.nan] * num_rows
        G = [np.nan] * num_rows  # pylint:disable=invalid-name
        Gbp = [np.nan] * num_rows  # pylint:disable=invalid-name
        Grp = [np.nan] * num_rows  # pylint:disable=invalid-name
        for idx, e in enumerate(self.simbad_table['GaiaID']):
            match = np.where(e == self.gaia_by_name['designation'])[0]
            if len(match):
                row = self.gaia_by_name[match[0]]
                col[idx] = row['Gbp-Grp']
                G[idx] = row['G']
                Gbp[idx] = row['Gbp']
                Grp[idx] = row['Grp']        
        
        self.simbad_table['Gbp-Grp'] = col
        self.simbad_table['G'] = G
        self.simbad_table['Gbp'] = Gbp
        self.simbad_table['Grp'] = Grp
        
        # cross-match
        #self.cross_match_and_extend()

    def cross_match_and_extend(self) -> None:
        """Cross-match SIMBAD and Gaia stars and extend the simbad table"""
        # TODO: test this

        s_radec = np.array([[e['ra'], e['dec']] for e in self.simbad_table])
        g_radec = np.array([[e['ra'], e['dec']] for e in self.gaia_by_fov])
        
        m = self.cross_match_and_get_colour(s_radec, g_radec).transpose()
        missing = np.isnan(self.simbad_table['Gbp-Grp'])
        self.simbad_table[missing]['Gbp-Grp'] = m[0][missing]
        self.simbad_table[missing]['G'] = m[1][missing]
        self.simbad_table[missing]['Gbp'] = m[2][missing]
        self.simbad_table[missing]['Grp'] = m[3][missing]

    def cross_match_and_get_colour(self, a1: np.ndarray, a2: np.ndarray, tolerance: float = 0.01) -> np.ndarray:
        """Cross match two 2d arrays and return closest match up to tolerance"""
        # TODO: test this

        cols = []
        for s in a1:
            dist = np.linalg.norm(s - a2, axis=1) 
            closest = np.argmin(dist)
            if dist[closest] < tolerance:
                cols.append([self.gaia_by_fov[closest]['Gbp-Grp'], self.gaia_by_fov[closest]['G'], self.gaia_by_fov[closest]['Gbp'], self.gaia_by_fov[closest]['Grp']])
            else:
                cols.append([np.nan, np.nan, np.nan, np.nan])
        return np.array(cols)

    def filter_stars(self, filter_spec: List[GenericFilter]) -> Table:
        """Give a list of min-max filter specifications, return the table with the matching data.

        Args:
            filter_spec (List[MinMaxValue]): List of min-max filter specifications.

        Returns:
            Table: table with the matching data
        """
        fvs = [True] * len(self.simbad_table)
        main_star = self.simbad_table['Object'] == self.simbad_table[0]['Object']
        all_false = [False] * len(self.simbad_table)
        for f in filter_spec:
            if isinstance(f, FilterMinMaxValue):
                f1 = self.simbad_table[f.var_name] >= f.min_value
                f2 = self.simbad_table[f.var_name] <= f.max_value
                if f.allow_nan:
                    f3 = np.isnan(self.simbad_table[f.var_name])
                else:
                    f3 = all_false
                fvs = fvs & ((f1 & f2) | f3)
            elif isinstance(f, FilterNotValue):
                f1 = self.simbad_table[f.var_name] != f.not_value
                if f.allow_nan:
                    f3 = np.isnan(self.simbad_table[f.var_name])
                else:
                    f3 = all_false
                fvs = fvs & (f1 | f3)
            elif isinstance(f, FilterIsValue):
                f1 = self.simbad_table[f.var_name] == f.value
                if f.allow_nan:
                    f3 = np.isnan(self.simbad_table[f.var_name])
                else:
                    f3 = all_false
                fvs = fvs & (f1 | f3)
            elif isinstance(f, FilterOrIsValue):
                f1 = self.simbad_table[f.var_name] == f.value
                fvs = fvs | f1
        return self.simbad_table[main_star | fvs]
