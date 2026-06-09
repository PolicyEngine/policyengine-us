from policyengine_us.model_api import *


class in_ccdf_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Indiana CCDF weekly copayment"
    definition_period = MONTH
    defined_for = "in_ccdf_eligible"
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=39",
        "https://www.in.gov/fssa/carefinder/files/CCDFSlidingFeeSchedule_withCopays_2026.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.ccdf.copay
        # Income is floored at zero so a self-employment loss cannot produce a
        # negative copay.
        countable_income = max_(spm_unit("in_ccdf_countable_income", period), 0)
        fpg = spm_unit("spm_unit_fpg", period)
        fpg_ratio = where(fpg > 0, countable_income / fpg, 0)
        fee_factor = p.fee_factor.calc(fpg_ratio)
        return countable_income * fee_factor
