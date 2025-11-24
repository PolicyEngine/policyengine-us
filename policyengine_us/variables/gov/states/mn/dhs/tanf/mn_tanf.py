from policyengine_us.model_api import *


class mn_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP"
    unit = USD
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G/pdf"
    defined_for = "mn_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("mn_tanf_payment_standard", period)
        family_wage_level = spm_unit("mn_tanf_family_wage_level", period)
        countable_earned = spm_unit("mn_tanf_countable_earned_income", period)
        countable_unearned = spm_unit(
            "mn_tanf_countable_unearned_income", period
        )

        has_earnings = countable_earned > 0

        benefit_with_earnings = family_wage_level - countable_earned
        adjusted_payment_standard = payment_standard - countable_unearned

        benefit = where(
            has_earnings,
            min_(benefit_with_earnings, adjusted_payment_standard),
            adjusted_payment_standard,
        )

        return max_(benefit, 0)
