from policyengine_us.model_api import *


class vt_ccfap_family_share(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VT
    label = "Vermont CCFAP monthly family share (copayment)"
    reference = (
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/Benefits/CCFAP-Income-Guidelines.pdf",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=17",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.vt.dcf.ccfap
        income = spm_unit("vt_ccfap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        fpl_ratio = where(fpg > 0, income / fpg, 0)

        exempt = spm_unit("vt_ccfap_categorically_exempt", period)

        weekly_share = p.family_share.scale.calc(fpl_ratio)
        monthly_share = weekly_share * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        return where(exempt, 0, monthly_share)
