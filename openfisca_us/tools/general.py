from openfisca_core.model_api import *
from openfisca_us.entities import *
import numpy as np


def add(entity, period, *variables):
    return sum([entity(var, period) for var in variables])


def amount_between(x, lower, upper):
    return max_(min_(x, upper), lower) - lower


infinity = np.inf
