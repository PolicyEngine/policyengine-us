from policyengine_us.model_api import *


class mt_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = (
        "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF502.12.23.pdf#page=1"
    )

    adds = ["mt_tanf_earned_income_after_disregard_person"]
