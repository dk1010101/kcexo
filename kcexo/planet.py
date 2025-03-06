
import astropy.units as u
from astropy.time import Time

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
                 status: ExoClockStatus | None = None
                 ):
        self.host_star: Star = host_star
        self.name: str = name
        self.ephem_mid_time: Time = ephem_mid_time
        self.ephem_mid_time_e: u.Quantity["time"] = ephem_mid_time_e
        self.period: u.Quantity[u.day] = period
        self.RpRs: float = RpRs  # pylint:disable=invalid-name
        self.aRs: float = aRs  # pylint:disable=invalid-name
        self.i: u.Quantity[u.degree] = i
        self.depth: u.Quantity[u.mmag] = depth
        self.duration: u.Quantity[u.hour] = duration
        self.e: float = e
        self.omega: u.Quantity[u.deg] = omega
        self.period_e: u.Quantity[u.day] = period_e
        self.RpRs_e: float = RpRs_e  # pylint:disable=invalid-name
        self.aRs_e: float = aRs_e  # pylint:disable=invalid-name
        self.i_e: u.Quantity[u.degree] = i_e
        self.status: ExoClockStatus | None = status

    def __eq__(self, other: "Planet") -> bool:
        """simple equality check"""
        return all([
            self.host_star == other.host_star,
            self.name == other.name,
            self.ephem_mid_time == other.ephem_mid_time,
            self.ephem_mid_time_e == other.ephem_mid_time_e,
            self.period == other.period,
            self.RpRs == other.RpRs,
            self.aRs == other.aRs,
            self.i == other.i,
            self.depth == other.depth,
            self.duration == other.duration,
            self.e == other.e,
            self.omega == other.omega,
            self.period_e == other.period_e,
            self.RpRs_e == other.RpRs_e,
            self.aRs_e == other.aRs_e,
            self.i_e == other.i_e,
            self.status == other.status
        ])
