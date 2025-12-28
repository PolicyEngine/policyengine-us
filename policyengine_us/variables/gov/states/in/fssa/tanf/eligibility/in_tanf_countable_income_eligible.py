from policyengine_us.model_api import *


class in_tanf_countable_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana TANF countable income eligible"
    definition_period = MONTH
    reference = (
        "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4-1",
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-1-1.7",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # Initial: standard of need; Continuing: FPL * rate
        p = parameters(period).gov.states["in"].fssa.tanf
        countable = spm_unit(
            "in_tanf_countable_income_for_eligibility", period
        )
        is_enrolled = spm_unit("is_tanf_enrolled", period)

        fpg = spm_unit("tanf_fpg", period)
        continuing_threshold = fpg * p.eligibility.continuing.fpg_rate

        threshold = where(
            is_enrolled,
            continuing_threshold,
            spm_unit("in_tanf_payment_standard", period),
        )
        return countable < threshold
