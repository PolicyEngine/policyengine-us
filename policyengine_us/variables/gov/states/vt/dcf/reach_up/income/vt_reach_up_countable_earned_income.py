from policyengine_us.model_api import *


class vt_reach_up_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont Reach Up countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://law.justia.com/codes/vermont/title-33/chapter-11/section-1103/",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        earned_after_disregard = add(
            spm_unit, period, ["vt_reach_up_countable_earned_income_person"]
        )
        dependent_care = spm_unit(
            "vt_reach_up_dependent_care_deduction", period
        )
        return max_(earned_after_disregard - dependent_care, 0)
