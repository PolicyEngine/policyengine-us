from policyengine_us.model_api import *


class ut_fep_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utah Family Employment Program gross income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-200-239"
    defined_for = StateCode.UT

    adds = [
        "tanf_gross_earned_income",
        "tanf_gross_unearned_income",
    ]
