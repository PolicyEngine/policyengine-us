from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.entity.household import *  # not sure what I need here


class shelter_deduction(Variable):
    


class net_income(Variable):
    value_type = int
    entity = household
    definition_period = YEAR
    documentation

