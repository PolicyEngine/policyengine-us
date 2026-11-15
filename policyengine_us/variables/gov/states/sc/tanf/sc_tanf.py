from policyengine_us.model_api import *


class sc_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF"
    unit = USD
    definition_period = MONTH
    defined_for = "sc_tanf_eligible"
    reference = (
        # PDF pages 133-134
        "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=133",
        "https://www.scstatehouse.gov/coderegs/Chapter%20114.pdf#page=210",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf
        need_standard = spm_unit("sc_tanf_need_standard", period)
        countable_income = spm_unit("sc_tanf_countable_income", period)
        excess_income = max_(need_standard - countable_income, 0)
        benefit = excess_income * p.payment.rate
        # Cap benefit at need standard to prevent negative income
        # from inflating benefits above the maximum.
        # 114-1140(A)(4) rounds the payment down to the next lower whole
        # dollar, and the Section 8.15 table drops the cents of the payment
        # standard. Round before the minimum test: $9.79 becomes $9, which
        # pays nothing.
        capped_benefit = np.floor(min_(benefit, need_standard * p.payment.rate))
        # No payment is made in a month when the benefit is under the
        # minimum (S.C. Code Regs. 114-1140(A)(5); TANF Policy Manual 8.16 I).
        return where(capped_benefit >= p.minimum_payment, capped_benefit, 0)
