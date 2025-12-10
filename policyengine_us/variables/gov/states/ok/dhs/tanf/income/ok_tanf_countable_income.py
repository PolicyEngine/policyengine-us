from policyengine_us.model_api import *


class ok_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oklahoma TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-10-3-59"
    )
    defined_for = StateCode.OK
    # Per OAC 340:10-3-39: Unearned income counted at gross amount
    adds = ["ok_tanf_countable_earned_income", "tanf_gross_unearned_income"]
