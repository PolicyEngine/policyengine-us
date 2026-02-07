from policyengine_us.model_api import *


class ia_fip_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf#page=19"

    adds = ["ia_fip_countable_earned_income", "tanf_gross_unearned_income"]
