from policyengine_us.model_api import *


class me_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331",
    )
    defined_for = StateCode.ME

    def formula(spm_unit, period, parameters):
        # Per 22 M.R.S. Section 3762:
        # Countable income = earned (after disregards) + unearned - deductions
        p = parameters(period).gov.states.me.dhhs.tanf

        # Countable earned income (after $108 + 50% disregard)
        countable_earned = spm_unit("me_tanf_countable_earned_income", period)

        # Gross unearned income minus child support pass-through
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        child_support = add(spm_unit, period, ["child_support_received"])
        child_support_exclusion = min_(
            child_support, p.child_support_pass_through
        )
        countable_unearned = max_(gross_unearned - child_support_exclusion, 0)

        # Subtract child care deduction
        child_care_deduction = spm_unit("me_tanf_child_care_deduction", period)

        return max_(
            countable_earned + countable_unearned - child_care_deduction, 0
        )
