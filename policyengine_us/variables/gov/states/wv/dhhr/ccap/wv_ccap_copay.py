from policyengine_us.model_api import *


class wv_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "West Virginia CCAP family co-payment"
    definition_period = MONTH
    defined_for = StateCode.WV
    reference = (
        "https://bfa.wv.gov/media/6826/download?inline#page=1",
        "https://bfa.wv.gov/media/6766/download?inline#page=65",
        "https://bfa.wv.gov/media/39915/download?inline#page=40",
    )

    def formula(spm_unit, period, parameters):
        # NOTE: %-of-income approximation of the 176-cell sliding fee scale
        # (Appendix A), calibrated to the 3-person family column. Per Manual
        # §6.4.3, the actual fee is charged per child up to 3 children — we
        # apply that multiplier here. The 7% cap and <40% FPL waiver are in
        # the rate schedule; foster waiver overrides below.
        p = parameters(period).gov.states.wv.dhhr.ccap.copayment
        countable_income = spm_unit("wv_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        fpl_ratio = where(fpg > 0, countable_income / max_(fpg, 1), 0)
        per_child_rate = p.rate.calc(fpl_ratio)
        num_eligible_children = add(spm_unit, period, ["wv_ccap_eligible_child"])
        billed_children = min_(num_eligible_children, p.max_billed_children)
        uncapped_copay = countable_income * per_child_rate * billed_children
        capped_copay = min_(uncapped_copay, countable_income * p.max_share)
        has_foster_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        return where(has_foster_child, 0, capped_copay)
