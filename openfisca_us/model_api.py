from functools import reduce
from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from pathlib import Path
from openfisca_us.typing import *

REPO = Path(__file__).parent


def all_of_variables(variables: List[str]) -> Formula:
    def formula(entity, period, parameters):
        value = True
        for variable in variables:
            value = value & (add(entity, period, [variable]) > 0)
        return value

    return formula
