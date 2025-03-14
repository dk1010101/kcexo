# -*- coding: UTF-8 -*-
# cSpell:ignore kcexo
"""Package for the json/yaml schemas"""

from importlib.resources import files
import json

observatories_schema=json.loads(files('kcexo.schema').joinpath('observatory.json').read_text())

__all__ = [
    'observatories_schema'
]
