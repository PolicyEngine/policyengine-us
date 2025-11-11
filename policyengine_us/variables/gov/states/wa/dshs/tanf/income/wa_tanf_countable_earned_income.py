from policyengine_us.model_api import *


class wa_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = ("https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0170",)
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # Get gross earned income from federal TANF variable
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])

        # Apply earned income disregard per WAC 388-450-0170:
        # "We start by deducting the first $500 of the total household's
        # earned income. We then subtract 50% of the remaining monthly
        # gross earned income."
        p = parameters(period).gov.states.wa.dshs.tanf.income

        # Step 1: Deduct flat $500 family earnings disregard
        remainder_after_flat_disregard = max_(
            gross_earned - p.earned_income_disregard, 0
        )

        # Step 2: Count 50% of remaining income (disregard other 50%)
        # "Work incentive percentage" = what we COUNT (not what we disregard)
        countable_earned = (
            remainder_after_flat_disregard * p.work_incentive_percentage
        )

        return countable_earned
