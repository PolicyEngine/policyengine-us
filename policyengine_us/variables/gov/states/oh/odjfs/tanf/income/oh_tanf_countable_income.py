from policyengine_us.model_api import *


class oh_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio TANF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5107.10",
        "http://codes.ohio.gov/oac/5101:1-23-20",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Get gross earned income - aggregate from federal sources
        gross_earned = spm_unit.sum(
            person("employment_income", period)
            + person("self_employment_income", period)
        )

        # Apply earned income disregard: $250 + 50% of remainder
        # ORC 5107.10(D)(3) specifies "the two hundred-fifty dollar and
        # one-half of the remainder disregards"
        p = parameters(period).gov.states.oh.odjfs.tanf.income.deductions
        disregard = p.earned_income_disregard
        flat_disregard = disregard.flat_amount

        # Calculate remainder after flat disregard
        remainder = max_(gross_earned - flat_disregard, 0)

        # Apply percentage disregard to remainder
        percent_disregarded = remainder * disregard.percent_of_remainder

        # Countable earned income = gross - flat disregard - percent of remainder
        countable_earned = max_(
            gross_earned - flat_disregard - percent_disregarded, 0
        )

        # Get gross unearned income from federal variable
        # Per ORC 5107.10(D)(3): "No disregards apply to gross unearned income"
        gross_unearned = spm_unit.sum(
            person("tanf_gross_unearned_income", period)
        )

        # Total countable income
        return countable_earned + gross_unearned
