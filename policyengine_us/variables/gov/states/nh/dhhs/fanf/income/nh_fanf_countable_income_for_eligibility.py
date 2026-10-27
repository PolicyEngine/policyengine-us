from policyengine_us.model_api import *


class nh_fanf_countable_income_for_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Hampshire FANF countable income for eligibility determination"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://gc.nh.gov/rules/state_agencies/he-w600.html",
        "https://www.dhhs.nh.gov/fam_htm/html/603_01_earned_income_disregards_eid_fam.htm",
        "https://www.dhhs.nh.gov/fam_htm/html/611_01_computing_eligibility_fam.htm",
    )
    defined_for = StateCode.NH

    adds = [
        "nh_fanf_countable_earned_income_for_eligibility",
        "tanf_gross_unearned_income",
    ]
