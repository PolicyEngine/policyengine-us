from policyengine_us.model_api import *


class nj_wfnj_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey WFNJ countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-3",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-8",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-1",
    )

    adds = [
        "nj_wfnj_countable_earned_income_person",
        "nj_wfnj_countable_unearned_income",
    ]
