from policyengine_us.model_api import *


class il_base_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL base income"
    unit = USD
    definition_period = YEAR

    adds = ["adjusted_gross_income", "il_base_income_additions"]
    subtracts = ["il_base_income_subtractions"]
