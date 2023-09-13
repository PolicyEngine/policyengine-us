from policyengine_us.model_api import *


class hi_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii child and dependent care credit"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=40"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.cdcc
        agi = tax_unit("hi_agi", period)
        rate = p.rate.calc(agi, right=True)

        # The smaller of the minimum earnings or dependent care benefits is used for the final calculation
        min_earned = min_(
            tax_unit("hi_dependent_care_benefits", period),
            tax_unit("hi_min_head_spouse_earned", period),
        )

        return rate * min_earned
