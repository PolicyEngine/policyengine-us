from policyengine_us.model_api import *


class mn_mfip_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable earned income for benefit calculation"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256P.03#stat.256P.03.2",
        "https://www.revisor.mn.gov/statutes/cite/142G.17#stat.142G.17.7",
    )
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        # Per MN Stat. 142G.17, Subd. 7 (benefit calculation):
        # Dependent care deduction does NOT apply to benefit calculation.
        # Only apply $65 per wage earner and 50% disregard.
        p = parameters(
            period
        ).gov.states.mn.dcyf.mfip.income.earned_income_disregard

        # Get gross earned income per person and sum
        person = spm_unit.members
        gross_earned_person = person("tanf_gross_earned_income", period)
        gross_earned = spm_unit.sum(gross_earned_person)

        # Count wage earners (persons with earned income > 0)
        has_earnings = gross_earned_person > 0
        num_wage_earners = spm_unit.sum(has_earnings)

        # Apply $65 per wage earner
        flat_disregard = p.flat_amount * num_wage_earners
        after_flat = max_(gross_earned - flat_disregard, 0)

        # Apply 50% disregard
        return after_flat * (1 - p.rate)
