from openfisca_us.model_api import *


class qualified_retirement_penalty(Variable):
    value_type = float
    entity = TaxUnit
    label = "Penalty tax on qualified retirement plans"
    unit = USD
    definition_period = YEAR
