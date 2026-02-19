from policyengine_us.model_api import *


class sc_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF"
    unit = USD
    definition_period = MONTH
    defined_for = "sc_tanf_eligible"
    reference = "https://dss.sc.gov/media/ojqddxsk/tanf-policy-manual-volume-65.pdf#page=131"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf
        # Compute need standard based on federal poverty guidelines
        fpg = spm_unit("tanf_fpg", period)
        need_standard = fpg * p.income.need_standard.rate
        countable_income = spm_unit("sc_tanf_countable_income", period)
        excess_income = max_(need_standard - countable_income, 0)
        benefit = excess_income * p.payment.rate
        # Cap benefit at need standard to prevent negative income
        # from inflating benefits above the maximum.
        return min_(benefit, need_standard * p.payment.rate)
