from policyengine_us.model_api import *


class mn_mfip_countable_income_for_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable income for eligibility"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/142G.16#stat.142G.16.1"
    )
    defined_for = StateCode.MN
    adds = [
        "mn_mfip_countable_earned_income_for_eligibility",
        "mn_mfip_countable_unearned_income",
    ]
