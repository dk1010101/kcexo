from importlib.resources import files
import json


observatories_schema=json.loads(files('kcexo.schema').joinpath('observatory.json').read_text())
