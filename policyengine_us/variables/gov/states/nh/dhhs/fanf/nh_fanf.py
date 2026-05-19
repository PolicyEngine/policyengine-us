from policyengine_us.model_api import *


class nh_fanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Hampshire Financial Assistance to Needy Families"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://gc.nh.gov/rsa/html/xii/167/167-77-g.htm",
        "https://www.dhhs.nh.gov/sr_htm/html/sr_97-03_dated_02_97.htm",
    )
    defined_for = "nh_fanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("nh_fanf_payment_standard", period)
        countable_income = spm_unit("nh_fanf_countable_income", period)
        benefit = max_(payment_standard - countable_income, 0)
        return min_(benefit, payment_standard)
