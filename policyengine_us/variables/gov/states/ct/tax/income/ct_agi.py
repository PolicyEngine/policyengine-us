from policyengine_us.model_api import *


class ct_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    adds = ["adjusted_gross_income", "ct_agi_additions"]
    subtracts = ["ct_agi_subtractions"]
