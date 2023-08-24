from policyengine_us.model_api import *


class co_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado subtractions from federal taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
