from policyengine_us.model_api import *


class oh_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio TANF countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5107.10",
        "http://codes.ohio.gov/oac/5101:1-23-20",
    )

    def formula(spm_unit, period, parameters):
        # Get gross earned income and convert to monthly for calculation
        gross_earned_annual = spm_unit("oh_tanf_gross_earned_income", period)
        gross_earned_monthly = gross_earned_annual / MONTHS_IN_YEAR

        # Apply earned income disregard: $250 + 50% of remainder
        # ORC 5107.10(D)(3) specifies "the two hundred-fifty dollar and
        # one-half of the remainder disregards"
        p = parameters(period).gov.states.oh.odjfs.tanf.earned_income_disregard

        # Use monthly disregard amounts
        flat_disregard = p.flat_amount

        # Calculate remainder after flat disregard
        remainder = max_(gross_earned_monthly - flat_disregard, 0)

        # Apply percentage disregard to remainder
        percent_disregarded = remainder * p.percent_of_remainder

        # Countable earned income = gross - flat disregard - percent of remainder
        countable_earned_monthly = max_(
            gross_earned_monthly - flat_disregard - percent_disregarded, 0
        )

        # Get gross unearned income and convert to monthly
        # Per ORC 5107.10(D)(3): "No disregards apply to gross unearned income"
        person = spm_unit.members
        gross_unearned_annual = spm_unit.sum(
            person("tanf_gross_unearned_income", period)
        )
        gross_unearned_monthly = gross_unearned_annual / MONTHS_IN_YEAR

        # Total monthly countable income
        monthly_countable = countable_earned_monthly + gross_unearned_monthly

        # Annualize for YEAR definition period
        return monthly_countable * MONTHS_IN_YEAR
