from policyengine_us.model_api import *


class wv_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for West Virginia CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.WV
    reference = (
        "https://bfa.wv.gov/media/6766/download?inline#page=25",
        "https://bfa.wv.gov/media/6826/download?inline#page=1",
    )

    def formula(spm_unit, period, parameters):
        # NOTE: We model the Appendix A intake cap (~185% FPL). The 85% SMI
        # "Over-Income Policy Exception" for enrolled recipients (Manual §4.7.1)
        # is not modeled at the moment. We also don't distinguish child-only
        # TANF cases (Manual §3.2.1.4 requires them to pass the FPL test) from
        # full TANF — is_tanf_enrolled treats both as categorically eligible.
        p = parameters(period).gov.states.wv.dhhr.ccap.income
        countable_income = spm_unit("wv_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        fpl_eligible = countable_income <= fpg * p.fpl_limit
        is_tanf = spm_unit("is_tanf_enrolled", period)
        return is_tanf | fpl_eligible
