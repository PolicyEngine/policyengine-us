from policyengine_us.model_api import *


class nh_fanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Hampshire FANF income eligible"
    definition_period = MONTH
    reference = (
        "https://gc.nh.gov/rsa/html/xii/167/167-77-g.htm",
        "https://www.dhhs.nh.gov/fam_htm/newfam.htm",
    )
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("nh_fanf_countable_income", period)
        payment_standard = spm_unit("nh_fanf_payment_standard", period)
        return countable_income <= payment_standard
