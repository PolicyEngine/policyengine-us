from policyengine_us.model_api import *


class taxsim_fiitax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal income tax"
    unit = USD
    definition_period = YEAR

    adds = ["income_tax"]
