from policyengine_us.model_api import *


class me_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331",
    )
    defined_for = StateCode.ME

    def formula(spm_unit, period, parameters):
        # Per 22 M.R.S. Section 3762(3)(B)(7-D):
        # Each employed person gets $108 flat + 50% disregard (applied per person)
        # Then child care deduction applies at household level
        earned_after_disregard = add(
            spm_unit, period, ["me_tanf_earned_income_after_disregard_person"]
        )

        # Subtract child care deduction (work-related expense)
        child_care_deduction = spm_unit("me_tanf_child_care_deduction", period)

        return max_(earned_after_disregard - child_care_deduction, 0)
