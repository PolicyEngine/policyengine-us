from policyengine_us.model_api import *


class sc_tanf_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF gross income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=102"

    adds = [
        "sc_tanf_gross_earned_income",
        "sc_tanf_gross_unearned_income",
    ]
