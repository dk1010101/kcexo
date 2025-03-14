# -*- coding: UTF-8 -*-
# cSpell:ignore kcexo
"""Main `kcexo` module with objects representing stars, planets, transits and observatories"""
from .version import version as __version__

from .star import Star
from .planet import Planet, ExoClockStatus
from .observatory import Observatories, Observatory

# Then you can be explicit to control what ends up in the namespace,
__all__ = [
    'Observatories', 
    'Observatory', 
    'Star', 
    'Planet', 
    'ExoClockStatus', 
]
