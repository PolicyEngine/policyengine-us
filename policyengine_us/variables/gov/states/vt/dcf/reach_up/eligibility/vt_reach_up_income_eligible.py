from policyengine_us.model_api import *


class vt_reach_up_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Vermont Reach Up income eligible"
    definition_period = MONTH
    reference = (
        "https://law.justia.com/codes/vermont/title-33/chapter-11/section-1103/",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("vt_reach_up_countable_income", period)
        payment_standard = spm_unit("vt_reach_up_payment_standard", period)
        return countable_income < payment_standard
