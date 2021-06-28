from openfisca_core.model_api import *
from openfisca_us.entities import *

def add(entity, period, *variables):
    return sum([entity(var, period) for var in variables])