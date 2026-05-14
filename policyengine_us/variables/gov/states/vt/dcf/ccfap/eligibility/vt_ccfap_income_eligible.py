from policyengine_us.model_api import *


class vt_ccfap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    defined_for = StateCode.VT
    label = "Income eligible for Vermont CCFAP"
    reference = (
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=9",
        "https://dcf.vermont.gov/benefits/ccfap/act76-faqs",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.vt.dcf.ccfap.income
        countable_income = spm_unit("vt_ccfap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        income_limit = fpg * p.fpl_limit
        return countable_income <= income_limit
