from policyengine_us.model_api import *


class hi_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
