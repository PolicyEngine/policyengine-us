from openfisca_us.model_api import *


class taxsim_siitax(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax liability"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(["state_income_tax"])
