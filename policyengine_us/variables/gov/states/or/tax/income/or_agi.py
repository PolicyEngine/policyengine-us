from policyengine_us.model_api import *


class or_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR
    adds = ["adjusted_gross_income", "or_income_additions"]
    subtracts = ["or_income_subtractions"]
