# -*- coding: UTF-8 -*-
import logging
from typing import List

import astropy.units as u
from astropy.time import Time

from kcexo.star import Star
from kcexo.observatory import Observatory


class Transit():
    """Representation of a transit"""
    
    TRANSIT_MARGIN: u.Quantity["time"] = 10 * u.min
    
    def __init__(self,
                 pre_ingress: Time,
                 ingress: Time,
                 mid: Time,
                 egress: Time,
                 post_egress: Time,
                 t12: u.Quantity["time"],
                 depth: u.Quantity,
                 host_star: Star,
                 observer: Observatory,
                 do_not_adjust_for_barycenter: bool = False) -> None:
        """Initialisation of the transit object.

        Args:
            pre_ingress (Time): `t1` - `pre ingress duration`
            ingress (Time): `t1`
            mid (Time): `t mid`
            egress (Time): `t4`
            post_egress (Time): `t4` + `post ingress duration`
            t12 (u.Quantity['time']): duration between `t1` and `t2` (and `t3` and `t4` which is super super close so taken to be identical)
            depth (u.Quantity): Depth of the transit
            host_star (Star): Star which the transiting planet orbits
            observer (Observatory): Observatory/Instrument
            do_not_adjust_for_barycenter (bool, optional): Should we *not* adjust of the barycentric times? Defaults to False meaning that we will adjust.
        """
        self.log = logging.getLogger()

        self.meridian_crossing: Time
        self.twilight_e: List[Time] = []
        self.twilight_m: List[Time] = []
        self.has_meridian_crossing: bool
        self.problem_meridian_crossing: bool
        self.problem_twilight_civil: bool
        self.problem_twilight_nautical: bool
        self.problem_twilight_astronomical: bool
        
        self.host_star: Star = host_star
        self.pre_ingress: Time = pre_ingress
        self.ingress: Time = ingress
        self.mid: Time = mid
        self.egress: Time = egress
        self.post_egress: Time = post_egress
        self.t12: u.Quantity["time"] = t12
        self.depth: u.Quantity = depth
        self.observatory: Observatory = observer
        
        if not do_not_adjust_for_barycenter:
            self._adjust_for_barycenter()
        
        self._set_meridian()
        self._set_twilight()      

    def _adjust_for_barycenter(self) -> None:
        """Transit times we get from `astroplan` are not adjusted for the time it takes 
        light to travel from the barycentre to the observer so this functions adjusts for that.

        """
        self.pre_ingress       -= self.pre_ingress.light_travel_time(self.host_star.c, kind='barycentric', location=self.observatory.location)
        self.ingress           -= self.ingress.light_travel_time(self.host_star.c, kind='barycentric', location=self.observatory.location)
        self.mid               -= self.mid.light_travel_time(self.host_star.c, kind='barycentric', location=self.observatory.location)
        self.egress            -= self.egress.light_travel_time(self.host_star.c, kind='barycentric', location=self.observatory.location)
        self.post_egress       -= self.post_egress.light_travel_time(self.host_star.c, kind='barycentric', location=self.observatory.location)

    def _set_meridian(self) -> None:
        """If the meridian flip will take place between t1 and t2 or between t3 and t4 then we have a problem.
        
        We also need to take in to account the fact that flips take time so we cannot have a flip execution to fall between t12 or t34. We also
        can't flip at t2 or t4 so we add (arbitrary) 10min margin as we need to make sure that the transit data is there for the detections to
        be possible.
        """
        self.meridian_crossing = self.observatory.observer.target_meridian_transit_time(self.pre_ingress, self.host_star.target, 'nearest', n_grid_points=10)
        
        # if meridian flip will happen get a more accurate value
        if (self.pre_ingress - self.TRANSIT_MARGIN) <= self.meridian_crossing <= (self.post_egress + self.TRANSIT_MARGIN):
            self.meridian_crossing = self.observatory.observer.target_meridian_transit_time(self.pre_ingress, self.host_star.target, 'nearest', n_grid_points=300)
        
        t1 = self.ingress
        t2 = t1 + self.t12.to(u.hour)
        t3 = self.egress - self.t12.to(u.hour)
        t4 = self.egress
        
        t1_wm = t1 - self.observatory.meridian_crossing_duration - self.TRANSIT_MARGIN
        t2_wm = t2 + self.TRANSIT_MARGIN
        t3_wm = t3 - self.observatory.meridian_crossing_duration - self.TRANSIT_MARGIN
        t4_wm = t4 + self.TRANSIT_MARGIN
        
        self.has_meridian_crossing = (t1_wm <= self.meridian_crossing <= t4_wm)  # pylint:disable=superfluous-parens
        self.problem_meridian_crossing = (t1_wm <= self.meridian_crossing <= t2_wm) or (t3_wm <= self.meridian_crossing <= t4_wm)

    def _set_twilight(self) -> None:
        """Save when twilights are and also if they are going to be a problem."""
        self.twilight_e, self.twilight_m = self.observatory.get_twilights(self.pre_ingress, self.post_egress)
        self.problem_twilight_astronomical = False
        self.problem_twilight_nautical = False
        self.problem_twilight_civil = False
        
        if (
            (
                (self.twilight_e[0] is not None and self.twilight_e[1] is not None) and 
                (self.twilight_e[0] <= self.pre_ingress <= self.twilight_e[1])
            ) or
            (
                (self.twilight_m[2] is not None and self.twilight_m[3] is not None) and 
                (self.twilight_m[2] <= self.post_egress <= self.twilight_m[3])
            )
           ):
            self.problem_twilight_civil = True
        if (
            (
                (self.twilight_e[1] is not None and self.twilight_e[2] is not None) and 
                (self.twilight_e[1] <= self.pre_ingress <= self.twilight_e[2])
            ) or 
            (
                (self.twilight_m[1] is not None and self.twilight_m[2] is not None) and 
                (self.twilight_m[1] <= self.post_egress <= self.twilight_m[2])
            )
           ):
            self.problem_twilight_nautical = True
        if (
            (
                (self.twilight_e[2] is not None and self.twilight_e[3] is not None) and 
                (self.twilight_e[2] <= self.pre_ingress <= self.twilight_e[3])
            ) or
            (
                (self.twilight_m[0] is not None and self.twilight_m[1] is not None) and 
                (self.twilight_m[0] <= self.post_egress <= self.twilight_m[1])
            )
           ):
            self.problem_twilight_astronomical = True

    def __str__(self):
        s = f"Transit [{self.host_star.name} {self.observatory.observer.name} "
        s += f"({self.pre_ingress.iso[:16]}, {self.ingress.iso[:16]}, {self.mid.iso[:16]}, {self.egress.iso[:16]}, {self.post_egress.iso[:16]}) "
        s += f"t12={str(self.t12)} "
        s += f"depth={str(self.depth)} "
        s += f"|{Transit._t(self.problem_meridian_crossing)}|"
        s += f"{Transit._t(self.problem_twilight_astronomical)}"
        s += f"{Transit._t(self.problem_twilight_nautical)}"
        s += f"{Transit._t(self.problem_twilight_civil)}| ]"
        return s
        
    def __repr__(self):
        return str(self)

    def as_list(self) -> List[Time]:
        """Return the transit times as a list."""
        return [
            self.pre_ingress,
            self.ingress,
            self.mid,
            self.egress,
            self.post_egress
        ]
        
    def t12345_as_list(self) -> List[Time]:
        """Return the transit times as a list."""
        return [
            self.pre_ingress,
            self.ingress,
            self.ingress + self.t12,
            self.egress - self.t12,
            self.egress,
            self.post_egress
        ]
        
    @staticmethod
    def _t(v: bool) -> str:
        if v:
            return '+'
        else:
            return '.'
