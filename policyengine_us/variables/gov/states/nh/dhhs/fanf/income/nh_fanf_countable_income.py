from policyengine_us.model_api import *


class nh_fanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Hampshire FANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.dhhs.nh.gov/sr_htm/html/sr_97-03_dated_02_97.htm",
        "https://www.dhhs.nh.gov/fam_htm/newfam.htm",
    )
    defined_for = StateCode.NH

    adds = ["nh_fanf_countable_earned_income", "tanf_gross_unearned_income"]
