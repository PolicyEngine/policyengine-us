from policyengine_us.model_api import *


class nh_fanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Hampshire FANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = "https://gc.nh.gov/rsa/html/xii/167/167-77-g.htm"
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.fanf.payment_standard
        annual_fpg = spm_unit("spm_unit_fpg", period.this_year)
        return annual_fpg * p.fpg_rate / MONTHS_IN_YEAR
