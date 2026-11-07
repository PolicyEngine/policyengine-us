from policyengine_us.model_api import *


class wv_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for West Virginia CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.WV
    reference = (
        "https://bfa.wv.gov/media/6766/download?inline#page=25",
        # PDF pages 1 and 5-6
        "https://bfa.wv.gov/media/6826/download?inline#page=1",
    )

    def formula(spm_unit, period, parameters):
        # NOTE: The 85% SMI "Over-Income Policy Exception" for enrolled recipients
        # (Manual §4.7.1) is not modeled at the moment. We also don't distinguish
        # child-only TANF cases (Manual §3.2.1.4 requires them to pass the FPL
        # test) from full TANF — is_tanf_enrolled treats both as categorically
        # eligible.
        p = parameters(period).gov.states.wv.dhhr.ccap.income
        countable_income = spm_unit("wv_ccap_countable_income", period)
        # Appendix A caps intake at 185% of the guideline, and each scale stops at
        # 85% of the state median income, which binds from ten people ($9,247 a
        # month). Appendix A prints each limit to the nearest dollar. Round to
        # cents first so floating-point noise can't move a tie.
        fpl_limit = np.floor(
            np.round(spm_unit("wv_ccap_fpg", period) * p.fpl_limit, 2) + 0.5
        )
        smi_limit = np.floor(
            np.round(spm_unit("wv_ccap_smi", period) * p.smi_limit, 2) + 0.5
        )
        income_eligible = countable_income <= min_(fpl_limit, smi_limit)
        is_tanf = spm_unit("is_tanf_enrolled", period)
        return is_tanf | income_eligible
