# -*- coding: UTF-8 -*-
from .version import version as __version__

from .star import Star
from .planet import Planet, ExoClockStatus
from .observatory import Observatories, Observatory
from .source.exoclock import ExoClock as ExoClockSource

# Then you can be explicit to control what ends up in the namespace,
__all__ = [
    'Observatories', 
    'Observatory', 
    'Star', 
    'Planet', 
    'ExoClockStatus', 
    'ExoClockSource'
]
