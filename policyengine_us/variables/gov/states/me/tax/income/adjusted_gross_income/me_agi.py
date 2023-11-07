from policyengine_us.model_api import *


class me_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_dwnld_ff.pdf"

    adds = ["adjusted_gross_income", "me_agi_additions"]
    subtracts = ["me_agi_subtractions"]
