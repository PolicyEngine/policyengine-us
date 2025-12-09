from policyengine_us.model_api import *


class wa_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0170"
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # Get gross earned income from federal TANF variable
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])

        # Apply earned income disregard per WAC 388-450-0170:
        # "We start by deducting the first $500 of the total household's
        # earned income. We then subtract 50% of the remaining monthly
        # gross earned income."
        p = parameters(
            period
        ).gov.states.wa.dshs.tanf.income.deductions.earned_income_disregard

        # Step 1: Deduct flat $500 family earnings disregard
        remainder = max_(gross_earned - p.amount, 0)

        # Step 2: Subtract (disregard) 50% of remaining income
        # Per WAC 388-450-0170(3): "subtract 50% of the remaining...income"
        amount_disregarded = remainder * p.percentage_disregarded

        # Countable earned income = remainder - amount disregarded
        return remainder - amount_disregarded
