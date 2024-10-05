from policyengine_us.model_api import *


class taxsim_siitax(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax liability"
    unit = USD
    definition_period = YEAR

    adds = ["state_income_tax"]
