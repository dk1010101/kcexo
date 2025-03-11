# -*- coding: UTF-8 -*-
# cSpell:ignore isot
import logging
import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime

import astropy.units as u
from astropy.table import Table


class Source(ABC):
    """Abstract star catalogue."""
    name = ""
    
    def __init__(self, 
                 file_root: Path,
                 file_stem_override: str = "",
                 max_age: u.Quantity["time"] = 1 * u.day) -> None:
        """Initialise the catalogue and load the data.

        Args:
            file_root (Path): Directory where the catalogue file is
            file_stem_override (str, optional): The override of the file stem name. Default is "" meaning 'do not override'. Overrides are a **Bad Thing**(tm).
            max_age (u.Quantity['time'], optional): How old does the catalogue need to be before it is updated? Defaults to one day.

        Raises:
            FileNotFoundError: If the stem name has not been set. This is usually a programming problem as inheriting classes will (should) set this.
        """
        self.log = logging.getLogger()
        
        self.file_age: u.Quantity["time"]
        self.file_max_age: u.Quantity["time"] = max_age
        self.file_root: Path = file_root
        if not self.name:
            raise FileNotFoundError("Source file name has not been set!")
        self.file_stem = file_stem_override if file_stem_override else self.name
        self.file: Path = self.file_root.joinpath(self.file_stem+".pickle")
        self.file_loaded: bool = False

        self.data: dict | None = None
        self._load_data()

    def _load_data(self) -> None:
        """Load the data from wherever the data comes from"""
        if self.needs_updating():
            # fetch new file and pickle it
            self._load_data_from_remote()
            self.save()
        else:
            self.load()

    @abstractmethod
    def _load_data_from_remote(self) -> None:
        """Load data from the source and set the `self.data` attribute."""
        raise NotImplementedError("Doh!")

    def needs_updating(self) -> bool:
        """Given the age and current date/time, does the cache need updating?"""
        if self.file.is_file():
            self.load()
            return self.file_age > self.file_max_age.to(u.s).value
        else:
            self.data = {
                'update_dt': datetime.fromisoformat("1992-01-12 10:00"),  # important date! ;D
                'data': {}
            }
            return True
    
    def update_age(self) -> None:
        """Set the local age to zero and update the age table with the update time (now)."""
        self.data['update_dt'] = datetime.now()
    
    def save(self) -> None:
        """Update the age and then save the data to the file."""
        self.update_age()
        with open(self.file, "wb") as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)

    def load(self, force_load: bool = False) -> None:
        """Load the data from the cache file"""
        if self.data is None or not self.file_loaded or force_load:
            with open(self.file, "rb") as f:
                self.data = pickle.load(f)
            self.file_age = (datetime.now() - self.data['update_dt']).total_seconds()
            self.file_loaded = True


def fix_str_types(tab: Table) ->  None:
    """Helper function that replaces all 'O' types in a table (which are really strings) with string types.

    It is here as only data sources will need this. Perhaps it would be better off in some `util` module...
        
    Args:
        tab (Table): table to modify
    """
    for col in tab.colnames:
        t = tab.dtype[col]
        if t=='O':
            tab[col] = tab[col].astype('str')
