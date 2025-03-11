import copy
from pathlib import Path

from typing import List, Dict, Tuple

import numpy as np

import astropy.units as u
from astropy.time import Time
from astroplan import is_event_observable, AltitudeConstraint

from kcexo.source.exoclock import ExoClock
from kcexo.planet import Planet
from kcexo.observatory import Observatory
from kcexo.transit import Transit


class ExoClockData():
    
    def __init__(self,
                 file_root: Path,
                 max_age: u.Quantity["time"]):
        self.sc = ExoClock(file_root, max_age)
        self.sc.load()
        
        self.data: Dict[str, Planet] = {}
        for row in self.sc.data['data']:
            p = Planet.from_exoclock_js(row)
            self.data[p.name] = p
    
    def get_transits(self,
                     start_time: Time,
                     end_time: Time,
                     observatory: Observatory,
                     night_only: bool = True,
                     telescope_only: bool = True,
                     ) -> Dict[str, List[Transit]]:
        """Return a map from planet name to a 

        Args:
            start_time (Time): Transits start time
            end_time (Time): Transits end time
            observatory (Observatory): Location and the instrument that will be used.
            night_only (bool, optional): Should only night transits be listed? Defaults to True.
            telescope_only (bool, optional): Should only planets potentially visible with the equipment be listed. Defaults to True.
            
        Returns:
            Dict[str, Transit]: Mapping from planet name to transit objects
        """
        return {
            name: p.get_transits(start_time, end_time, observatory, night_only)
            for name, p in self.data.items()
            if (telescope_only and (p.status.min_aperture <= observatory.aperture)) or (not telescope_only)
        }
              
    def filter_transits(self,
                        all_transits: Dict[str, List[Transit]],
                        observatory: Observatory,
                        apply_horizon: bool = True,
                        apply_twilight: str = 'none',
                        include_meridian_flip: bool = True,
                        include_problem_meridian_flip: bool = True) -> Tuple[Dict[str, List[Transit]], List[str]]:
        """Filter transits by various parameters.

        Args:
            all_transits (Dict[str, List[Transit]]): Transits for each planet.
            observatory (Observatory): Location and the instrument that will be used.
            apply_horizon (bool, optional): Should horizon visibility be applied? Default it True.
            apply_twilight (bool, str): Which twilight should be applied. Default is 'none'. Acceptible twilights are 
                'astronomical', 'nautical', 'civil' and 'none'. Assumes `night_only==True` is 'none' is not used.
            include_meridian_flip (bool, options): Should meridian flips be included? Default is True.
            include_problem_meridian_flip (bool, options): Should *problematic* (ie occurring between T1 and T2 or T3 and T4) meridian flips be included? Default is True.

        Returns:
            Tuple[Dict[str, List[Transit]], List[str]]: A filtered list of transits for each planet and a list of planet names with visible transits. If a planet does not 
                have a visible transits the first map will map to an empty list.
        """
        transits = copy.deepcopy(all_transits)
        horizon_constraint = []
        if apply_horizon:
            horizon_constraint.append(observatory.horizon_constraint)
        else:
            horizon_constraint.append(AltitudeConstraint(20*u.deg))
        visible: List[str] = []
        for name, planet_transits in transits.items():
            new_transits = []
            for i, transit in enumerate(planet_transits):
                # we we don't want meridian flips and have them or if we are not ok with the twilight, skip this transit
                if (((not include_meridian_flip and transit.has_meridian_crossing) or 
                     (not include_problem_meridian_flip and transit.problem_meridian_crossing)) or
                    not self._twilight_is_ok(transit, apply_twilight)):
                    continue
                # if the transit is visible (given the horizon)
                if np.all(is_event_observable(horizon_constraint, observatory.observer, self.data[name].host_star.target, transit.as_list())):
                    new_transits.append(planet_transits[i])
            transits[name] = new_transits
            if new_transits:
                visible.append(name)
        return transits, visible

    def _twilight_is_ok(self,
                        transit: Transit, 
                        apply_twilight: str) -> bool:
        """Check if the twilight constraint is ok.

        Args:
            transit (Transit): Transit in question
            apply_twilight (str): which twilight? Acceptible twilights are 
                'astronomical', 'nautical', 'civil', 'none' or 'all'. If
                e.g. 'nautical' is passed in then 'nautical' and 'astronomical' are
                acceptable while 'civil' is not. If 'none' is passed in then none
                of twilights are ok. 'all' means that we don't care if it is day or night.
                Strictly speaking 'civil' and 'none' are the same in this context as
                day or night is filtered off elsewhere.

        Raises:
            ValueError: If the twilight is not one of 'astronomical', 'nautical', 'civil', 'none' or 'all'.

        Returns:
            bool: denoting if the twilight constraint has been satisfied
        """
        if apply_twilight not in ['all', 'civil']:
            if apply_twilight == 'astronomical':
                return not transit.problem_twilight_astronomical
            elif apply_twilight == 'nautical':
                return not transit.problem_twilight_nautical
            elif apply_twilight == 'none':
                return not transit.problem_twilight_civil and not transit.problem_twilight_nautical and not transit.problem_twilight_civil
            else:
                raise ValueError(f"Unknown twilight constraint: {apply_twilight}")
        else:
            return True
    