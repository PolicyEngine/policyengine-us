from policyengine_us.model_api import *


class sc_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = "https://dss.sc.gov/media/ojqddxsk/tanf-policy-manual-volume-65.pdf#page=131"

    adds = [
        "sc_tanf_countable_earned_income_person",
        "sc_tanf_gross_unearned_income",
    ]
