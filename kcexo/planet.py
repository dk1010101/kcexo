# -*- coding: UTF-8 -*-
# cSpell:ignore logg teff exoclock mmag
from typing import Dict, Any, List

import numpy as np

import astropy.units as u
from astropy.units import imperial
from astropy.time import Time
from astropy.coordinates import SkyCoord

from astroplan import EclipsingSystem

from kcexo.star import Star
from kcexo.observatory import Observatory
from kcexo.transit import Transit
from kcexo.calc.orbits import transit_t12
from kcexo.source.exoclock import exoclock_t_t, exoclock_to_u


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
            isinstance(other, ExoClockStatus),
            self.priority == other.priority,
            self.min_aperture == other.min_aperture,
            self.ec_observations == other.ec_observations,
            self.ec_observations_recent == other.ec_observations_recent,
            self.total_observations == other.total_observations,
            self.total_observations_recent == other.total_observations_recent,
            self.oc == other.oc
        ])
        
    def __str__(self):
        s = "Status ["
        s += f"min_ap={self.min_aperture}"
        s += f" ec_obs={self.ec_observations}"
        s += f" ec_obs_r={self.ec_observations_recent}"
        s += f" t_obs={self.total_observations}"
        s += f" t_obs_r={self.total_observations_recent}"
        s += f" oc={self.oc}"
        s += "]"
        return s
    
    def __repr__(self):
        return str(self)

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
        
        self.t12: u.Quantity['time']
        self._calculate_t12()

        # NB: this is barycentric!
        self.system_target: EclipsingSystem = EclipsingSystem(self.ephem_mid_time, self.period, self.duration, self.name, self.e, self.omega.to(u.rad).value)
        # TODO: remember that we will need to adjust for barycentric times later on

    def __eq__(self, other: "Planet") -> bool:
        """simple equality check"""
        return all([
            isinstance(other, Planet),
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
            Teff = obj['teff'] * exoclock_to_u(obj['teff_units']),
            Teff_e = obj['teff_e1'] * exoclock_to_u(obj['teff_units']),
            logg = obj['logg'] * exoclock_to_u(obj['logg_units']),
            logg_e = obj['logg_e1'] * exoclock_to_u(obj['logg_units']),
            FeH = obj['meta'] * exoclock_to_u(obj['meta_units']),
            FeH_e = obj['meta_e1'] * exoclock_to_u(obj['meta_units']),
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
            ephem_mid_time = exoclock_t_t(obj['ephem_mid_time'], obj['ephem_mid_time_format']),
            ephem_mid_time_e = obj['ephem_mid_time_e1'] * exoclock_to_u(obj['ephem_mid_time_units']),
            period = obj['ephem_period'] * exoclock_to_u(obj['ephem_period_units']),
            period_e = obj['ephem_period_e1'] * exoclock_to_u(obj['ephem_period_units']),
            RpRs = obj['rp_over_rs'] * exoclock_to_u(obj['rp_over_rs_units']),
            RpRs_e = obj['rp_over_rs_e1'] * exoclock_to_u(obj['rp_over_rs_units']),
            aRs = obj['sma_over_rs'] * exoclock_to_u(obj['sma_over_rs_units']),
            aRs_e = obj['sma_over_rs_e1'] * exoclock_to_u(obj['sma_over_rs_units']),
            i = obj['inclination'] * exoclock_to_u(obj['inclination_units']),
            i_e = obj['inclination_e1'] * exoclock_to_u(obj['inclination_units']),
            depth = obj['depth_r_mmag'] * u.mmag,
            duration = obj['duration_hours'] * u.hour,
            e = obj['eccentricity'],
            e_e = obj['eccentricity_e1'],
            omega = obj['periastron'] * exoclock_to_u(obj['periastron_units']),
            omega_e = obj['periastron_e1'] * exoclock_to_u(obj['periastron_units']),
            status = ecs
        )
        return p

    def _calculate_t12(self) -> None:
        """Calculate the time from the beginning of ingress/egress to the end.
        
        We use the same method here like ExoClock do where we solve the orbit for the values.
        This is easiest given that orbits with inclination, eccentricity and omega all make
        calcs rather unpleasant.
        
        Not for public use as the value will be calculated on instantiation and stored in `t12` attribute 
        which is easily accessible.

        """
        t12 = transit_t12(self.RpRs, self.period, self.aRs, self.e, self.i, self.omega)
        self.t12 = t12

    def get_transits(self, 
                     start_time: Time,
                     end_time: Time,
                     observatory: Observatory,
                     night_only: bool = True) -> List[Transit]:
        """Return all transits for a specific instrument (and thus observer) between specified dates.

        Note that all the times have been adjusted for barycentric coordinates.

        Args:
            start_time (Time): Start time
            end_time (Time): End time
            instrument (Instrument): Observer and the instrument
            night_only (bool, optional): Filter off anything that starts before sunset or ends after sunrise. Default is True.

        Returns:
            List[Transit]: List of transits
        """
        duration = (end_time - start_time).to(u.day)
        num_transits = int(np.ceil(duration / self.period))
        transits = self.system_target.next_primary_eclipse_time(start_time, num_transits)
        d: u.Quantity['time'] = self.duration / 2.0
        
        ret = []
        for mid_time in transits:
            t0 = mid_time - d - observatory.exo_hours_before
            t5 = mid_time + d + observatory.exo_hours_after
            if t5 <= end_time:
                if night_only:
                    sunset = observatory.observer.sun_set_time(t0)
                    sunrise = observatory.observer.sun_rise_time(t5)
                    if sunset >= t0 or sunrise <= t5:
                        continue
                tran = Transit(
                    pre_ingress = t0,
                    ingress = mid_time - d,
                    mid = mid_time,
                    egress = mid_time + d,
                    post_egress= t5,
                    t12=self.t12,
                    depth=self.depth,
                    host_star=self.host_star,
                    observer=observatory
                )
                ret.append(tran)
        return ret

    def __str__(self):
        s = f"Planet [{self.name} @ {self.host_star.name}"
        s += f" ephem_mid_time={self.ephem_mid_time}"
        s += f" period={self.period}"
        s += f" RpRs={self.RpRs}"
        s += f" aRs={self.aRs}"
        s += f" i={self.i}"
        s += f" depth={self.depth}"
        s += f" duration={self.duration}"
        s += f" e={self.e}"
        s += f" omega={self.omega}"
        s += f" ephem_mid_time_e={self.ephem_mid_time_e}"
        s += f" period_e={self.period_e}"
        s += f" RpRs_e={self.RpRs_e}"
        s += f" aRs_e={self.aRs_e}"
        s += f" i_e={self.i_e}"
        s += f" e_e={self.e_e}"
        s += f" omega_e={self.omega_e}"
        s += f" {self.status}"
        s += "]"
        return s
    
    def __repr__(self):
        return str(self)
