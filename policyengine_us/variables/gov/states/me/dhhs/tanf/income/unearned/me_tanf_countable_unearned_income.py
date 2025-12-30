from policyengine_us.model_api import *


class me_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331",
    )
    defined_for = StateCode.ME

    def formula(spm_unit, period, parameters):
        # Per 22 M.R.S. Section 3762: First $50/month of child support
        # is excluded from income calculations
        p = parameters(period).gov.states.me.dhhs.tanf

        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        child_support = add(spm_unit, period, ["child_support_received"])
        child_support_deduction = min_(
            child_support, p.child_support_deduction
        )

        return max_(gross_unearned - child_support_deduction, 0)
