from policyengine_us.model_api import *


class oh_owf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio OWF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5101:1-23-20",
    )

    def formula(spm_unit, period, parameters):
        # Get gross earned income from federal TANF variable
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])

        # Apply earned income disregard: $250 + 50% of remainder
        # ORC 5107.10(D)(3) specifies "the two hundred-fifty dollar and
        # one-half of the remainder disregards"
        p = parameters(
            period
        ).gov.states.oh.odjfs.owf.income.deductions.earned_income_disregard

        # Calculate remainder after flat disregard
        remainder = max_(gross_earned - p.flat_amount, 0)

        # Apply percentage disregard to remainder
        percent_disregarded = remainder * p.percentage_of_disregard

        # Countable earned income = gross - flat disregard - percent of remainder
        countable_earned = max_(remainder - percent_disregarded, 0)

        # Get gross unearned income from federal variable
        # Per ORC 5107.10(D)(3): "No disregards apply to gross unearned income"
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])

        # Total countable income
        return countable_earned + gross_unearned
