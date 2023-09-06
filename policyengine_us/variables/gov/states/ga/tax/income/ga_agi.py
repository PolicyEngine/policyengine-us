from policyengine_us.model_api import *


class ga_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
    adds = ["adjusted_gross_income", "ga_agi_additions"]
    subtracts = ["ga_agi_subtractions"]
