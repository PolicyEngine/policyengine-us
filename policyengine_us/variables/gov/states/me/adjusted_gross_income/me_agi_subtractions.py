from policyengine_us.model_api import *


class me_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "ME AGI subtractions"
    unit = USD
    documentation = "Subtractions from ME AGI over federal AGI."
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1s_ff.pdf"

    adds = [
        "tax_unit_taxable_social_security",
        "us_govt_interest",
        "me_pension_income_deduction",
    ]
