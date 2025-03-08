# cSpell:ignore Teff logg exoclock
from typing import Dict

import astropy.units as u
from astropy.coordinates import SkyCoord
from astroplan import FixedTarget


class Star():
    EQ_EXOCLOCK_ONLY: bool = True  #: should we check just exoclock JSON attributes?
    """Simple encapsulation of a star"""
    def __init__(self,
                 name: str,
                 c: SkyCoord,
                 parallax: u.Quantity[u.mas] | None = None,  # "angle (rad in si)"
                 pm_ra: u.Quantity[u.mas / u.year] | None = None,  # "rad/year"
                 pm_dec: u.Quantity[u.mas / u.year] | None = None,  # "rad/year"
                 mag: Dict[str, float] | None = None,
                 Teff: u.Quantity["temperature"] | None = None,  # pylint:disable=invalid-name
                 Teff_e: u.Quantity["temperature"] | None = None,  # pylint:disable=invalid-name
                 logg: u.Quantity[u.cm/u.s**2] | None = None,
                 logg_e: u.Quantity[u.cm/u.s**2] | None = None,
                 FeH: u.Quantity[u.dex] | None = None,  # pylint:disable=invalid-name
                 FeH_e: u.Quantity[u.dex] | None = None,  # pylint:disable=invalid-name
                 name_gaia: str = "",
                 name_2mass: str = "",
                 ):
        self.name_simbad: str = name
        self.name_gaia: str = name_gaia
        self.name_2mass: str = name_2mass
        self.c: SkyCoord = c
        self.parallax: u.Quantity | None = parallax
        self.pm_ra: u.Quantity | None = pm_ra
        self.pm_dec: u.Quantity | None = pm_dec
        self.mag: Dict[str, float] = mag if mag else {}
        self.Teff: u.Quantity["temperature"] | None = Teff  # pylint:disable=invalid-name
        self.Teff_e: u.Quantity["temperature"] = Teff_e if Teff_e is not None else 0.0 * u.K  # pylint:disable=invalid-name
        self.logg: u.Quantity[u.cm/u.s**2] | None = logg
        self.logg_e: u.Quantity[u.cm/u.s**2] = logg_e if logg_e is not None else 0.0 * u.cm/u.second**2
        self.FeH: u.Quantity[u.dex] | None = FeH  # pylint:disable=invalid-name
        self.FeH_e: u.Quantity[u.dex] = FeH_e if FeH_e  is not None else 0.0 * u.dex  # pylint:disable=invalid-name
        
        self.target: FixedTarget = FixedTarget(self.c, self.name)
        
    @property
    def name(self) -> str:
        """Alias for `name_simbad`"""
        return self.name_simbad

    @name.setter
    def name(self, s: str) -> None:
        """Name setter"""
        self.name_simbad = s

    def __eq__(self, other: "Star") -> bool:
        """Equality check.
        
        Note that is `EQ_EXOCLOCK_ONLY` is set to False (True is default) then
        equality is **non-associative** which could be a big problem! The only
        way to fix this is by setting `EQ_EXOCLOCK_ONLY` to false everywhere which
        is painful.
        """
        main_vars_eq = all([
            isinstance(other, Star),
            self.name_simbad == other.name_simbad,
            self.c == other.c,
            self.mag == other.mag,
            self.Teff == other.Teff,
            self.Teff_e == other.Teff_e,
            self.logg == other.logg,
            self.logg_e == other.logg_e,
            self.FeH == other.FeH,
            self.FeH_e == other.FeH_e,
        ])
        if not self.EQ_EXOCLOCK_ONLY:
            optional_vars_eq = all([
                self.name_gaia == other.name_gaia,
                self.name_2mass == other.name_2mass,
                self.parallax == other.parallax,
                self.pm_ra == other.pm_ra,
                self.pm_dec == other.pm_dec,    
            ])
        else:
            optional_vars_eq = True
        return main_vars_eq and optional_vars_eq
            
        
    def __str__(self) -> str:
        s = f"Star [{self.name_simbad} gaia={self.name_gaia} 2mass={self.name_2mass} "
        s += f"c={str(self.c)} (px={self.parallax} ra={self.pm_ra} dec={self.pm_dec}) "
        s += f"mag={self.mag} Teff={self.Teff}+-{self.Teff_e} logg={self.logg}+_{self.logg_e} FeH={self.FeH}+-{self.FeH_e}]"
        return s
    
    def __repr__(self) -> str:
        return str(self)
