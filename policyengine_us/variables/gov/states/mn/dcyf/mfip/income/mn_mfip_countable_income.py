from policyengine_us.model_api import *


class mn_mfip_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G/pdf"
    defined_for = StateCode.MN
    adds = [
        "mn_mfip_countable_earned_income",
        "mn_mfip_countable_unearned_income",
    ]
