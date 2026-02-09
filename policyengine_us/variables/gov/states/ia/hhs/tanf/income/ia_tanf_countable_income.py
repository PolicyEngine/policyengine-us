from policyengine_us.model_api import *


class ia_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"
    defined_for = StateCode.IA
    adds = [
        "ia_tanf_countable_earned_income",
        "ia_tanf_countable_unearned_income",
    ]
