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
        # Per 22 M.R.S. Section 3762(3)(B)(7-D): Month 7+ disregard
        # Step 1: Flat deduction of $108
        # Step 2: 50% disregard of remaining earnings
        # NOTE: First 6 months of employment have higher disregards (100%/75%)
        # that cannot be tracked in PolicyEngine
        p = parameters(period).gov.states.me.dhhs.tanf.earned_income

        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])

        # Apply flat deduction first
        after_flat = max_(gross_earned - p.flat_deduction, 0)

        # Apply percentage disregard (50% excluded = 50% counted)
        return after_flat * (1 - p.percentage_disregard)
