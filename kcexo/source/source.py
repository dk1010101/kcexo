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
    """Abstract star catalog."""
    name = ''
    
    def __init__(self, 
                 file_root: Path,
                 max_age: u.Quantity["time"] = 1 * u.day) -> None:
        self.log = logging.getLogger()
        
        self.file_age: u.Quantity["time"]
        self.file_max_age: u.Quantity["time"] = max_age
        self.file_root: Path = file_root
        if not self.name:
            raise FileNotFoundError("Source file name has not been set!")
        self.file: Path = self.file_root.joinpath(self.name+".pickle")
        self.file_loaded: bool = False

        self.data: dict | None = None
        self._load_data()

    @abstractmethod
    def _load_data(self) -> None:
        raise NotImplementedError("Doh!")

    def needs_updating(self) -> bool:
        """Give the age and date/time, does the cache need updating?"""
        if self.file.is_file():
            self.load()
            return self.file_age > self.file_max_age.to(u.s).value
        else:
            self.data = {
                'update_dt': datetime.fromisoformat("1992-01-12 10:00"),  # important date! ;D
                'data': {}
            }
            self.update_age()
            return True
    
    def update_age(self) -> None:
        """Set the local age to zero and update the age table with the update time (now)."""
        self.data['update_dt'] = datetime.now()
    
    def save(self) -> None:
        """Save the data to the file."""
        self.update_age()
        with open(self.file, "wb") as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)

    def load(self, force_load: bool = False) -> None:
        """Load the data from the file"""
        if self.data is None or not self.file_loaded or force_load:
            with open(self.file, "rb") as f:
                self.data = pickle.load(f)
            self.file_age = (datetime.now() - self.data['update_dt']).total_seconds()
            self.file_loaded = True


def fix_str_types(tab: Table) ->  None:
    """Replace all 'O' types (which are really strings) with string types.
        
    Args:
        tab (Table): table to modify
    """
    for col in tab.colnames:
        t = tab.dtype[col]
        if t=='O':
            tab[col] = tab[col].astype('str')
