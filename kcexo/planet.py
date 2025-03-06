# cSpell:ignore logg teff exoclock mmag
from typing import Dict, Any
import astropy.units as u
from astropy.units import imperial
from astropy.time import Time
from astropy.coordinates import SkyCoord

from astroplan import EclipsingSystem, FixedTarget

from kcexo.star import Star


class ExoClockStatus():
    """Encapsulation of the ExoClock status"""
    def __init__(self,
                 priority: str,
                 min_aperture: u.Quantity["length"],
                 ec_observations: int,
                 ec_observations_recent: int,
                 total_observations: int,
                 total_observations_recent: int,
                 oc: u.Quantity["time"] | None
                 ):
        self.priority = priority
        self.min_aperture = min_aperture
        self.ec_observations = ec_observations
        self.ec_observations_recent = ec_observations_recent
        self.total_observations = total_observations
        self.total_observations_recent = total_observations_recent
        self.oc = oc
        
    def __eq__(self, other: "ExoClockStatus") -> bool:
        """simple equality check"""
        return all([
            self.priority == other.priority,
            self.min_aperture == other.min_aperture,
            self.ec_observations == other.ec_observations,
            self.ec_observations_recent == other.ec_observations_recent,
            self.total_observations == other.total_observations,
            self.total_observations_recent == other.total_observations_recent,
            self.oc == other.oc
        ])

class Planet():
    """Encapsulation of an exo planet"""
    def __init__(self,
                 name: str,
                 host_star: Star,
                 ephem_mid_time: Time,
                 period: u.Quantity["time"],
                 RpRs: float,  # pylint:disable=invalid-name
                 aRs: float,  # pylint:disable=invalid-name
                 i: u.Quantity["angle"],
                 depth: u.Quantity[u.mmag],
                 duration: u.Quantity["time"],
                 e: float = 0.0,
                 omega: u.Quantity["angle"] = 0.0 * u.deg,
                 ephem_mid_time_e: u.Quantity["time"] = 0.0 * u.s,
                 period_e: u.Quantity["time"] = 0.0 * u.day,
                 RpRs_e: float = 0.0,  # pylint:disable=invalid-name
                 aRs_e: float = 0.0,  # pylint:disable=invalid-name
                 i_e: u.Quantity["angle"] = 0.0 * u.deg,
                 e_e: float = 0.0,
                 omega_e: u.Quantity["angle"] = 0.0 * u.deg,
                 status: ExoClockStatus | None = None
                 ):
        self.host_star: Star = host_star
        self.name: str = name
        self.ephem_mid_time: Time = ephem_mid_time
        self.ephem_mid_time_e: u.Quantity["time"] = ephem_mid_time_e
        self.period: u.Quantity["time"] = period
        self.period_e: u.Quantity["time"] = period_e
        self.RpRs: float = RpRs  # pylint:disable=invalid-name
        self.RpRs_e: float = RpRs_e  # pylint:disable=invalid-name
        self.aRs: float = aRs  # pylint:disable=invalid-name
        self.aRs_e: float = aRs_e  # pylint:disable=invalid-name
        self.i: u.Quantity["angle"] = i
        self.i_e: u.Quantity["angle"] = i_e
        self.depth: u.Quantity[u.mmag] = depth
        self.duration: u.Quantity["time"] = duration
        self.e: float = e
        self.e_e: float = e_e
        self.omega: u.Quantity["angle"] = omega
        self.omega_e: u.Quantity["angle"] = omega_e
        self.status: ExoClockStatus | None = status
        
        self.fixed_target = FixedTarget(self.host_star.c, self.host_star.name)
        # NB: this is barycentric!
        self.system = EclipsingSystem(self.ephem_mid_time, self.period, self.duration, self.name, self.e, self.omega.to(u.rad).value)
        # TODO: remember that we will need to adjust for barycentric times later on

    def __eq__(self, other: "Planet") -> bool:
        """simple equality check"""
        return all([
            self.host_star == other.host_star,
            self.name == other.name,
            self.ephem_mid_time == other.ephem_mid_time,
            self.ephem_mid_time_e == other.ephem_mid_time_e,
            self.period == other.period,
            self.period_e == other.period_e,
            self.RpRs == other.RpRs,
            self.RpRs_e == other.RpRs_e,
            self.aRs == other.aRs,
            self.aRs_e == other.aRs_e,
            self.i == other.i,
            self.i_e == other.i_e,
            self.depth == other.depth,
            self.duration == other.duration,
            self.e == other.e,
            self.e_e == other.e_e,
            self.omega == other.omega,
            self.omega_e == other.omega_e,
            self.status == other.status
        ])

    @staticmethod
    def from_exoclock_js(obj: Dict[str, Any]) -> "Planet":
        """Create a planet from exoclock json representation"""
        star_mag = {
            'V': obj['v_mag'],
            'R': obj['r_mag'],
            'G': obj['gaia_g_mag']
        }
        s = Star(
            name = obj['star'],
            c = SkyCoord(f"{obj['ra_j2000']} {obj['dec_j2000']}", unit=(u.hourangle, u.deg)),
            parallax = obj.get('parallax', 0.0) * u.mas,  # if missing we assume it is not moving...
            pm_ra = obj.get('pm_ra', 0.0) * u.mas/u.year,
            pm_dec = obj.get('pm_dec', 0.0) * u.mas/u.year,
            mag = star_mag,
            Teff = obj['teff'] * u.K,
            Teff_e = obj['teff_e1'] * u.K,
            logg = obj['logg'] * u.cm/u.s**2,
            logg_e = obj['logg_e1'] * u.cm/u.s**2,
            FeH = obj['meta'] * u.dex,
            FeH_e = obj['meta_e1'] * u.dex,
            name_gaia = obj.get('star_gaia', ''),
            name_2mass = obj.get('star_2mass', ''),
        )
        ecs = ExoClockStatus(
            priority = obj.get('priority', 'high'),
            min_aperture = obj.get('min_telescope_inches', 10_000) * imperial.inch,
            ec_observations = obj.get('exoclock_observations', 0),
            ec_observations_recent = obj.get('exoclock_observations_recent', 0),
            total_observations = obj.get('total_observations', 0),
            total_observations_recent = obj.get('total_observations_recent', 0),
            oc = obj.get('current_oc_min', 0.0) * u.minute,
        )
        p = Planet(
            name = obj['name'],
            host_star = s,
            ephem_mid_time = Time(js['ephem_mid_time'], format='js'),
            ephem_mid_time_e = obj['ephem_mid_time_e1'] * u.day,
            period = obj['ephem_period'] * u.day,
            period_e = obj['ephem_period_e1'] * u.day,
            RpRs = obj['rp_over_rs'],
            RpRs_e = obj['rp_over_rs_e1'],
            aRs = obj['sma_over_rs'],
            aRs_e = obj['sma_over_rs_e1'],
            i = obj['inclination'] * u.deg,
            i_e = obj['inclination_e1'] * u.deg,
            depth = obj['depth_r_mmag'] * u.mmag,
            duration = obj['duration'] * u.hour,
            e = obj['eccentricity'],
            e_e = obj['eccentricity_e1'],
            omega = obj['periastron'] * u.deg,
            omega_e = obj['periastron_e1'] * u.deg,
            status = ecs
        )
        return p
