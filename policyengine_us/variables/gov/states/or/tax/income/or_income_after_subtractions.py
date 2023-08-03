from policyengine_us.model_api import *


class or_income_after_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR income after subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR
    adds = ["or_income_after_additions"]
    subtracts = ["or_income_subtractions"]
