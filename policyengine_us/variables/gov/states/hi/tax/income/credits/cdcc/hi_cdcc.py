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
        # Schedule X PART II:
        # line 22 = min (line 19, line 20) = return of hi_dependent_care_benefits
        # min(line 23, line 24) = return of hi_cdcc_min_head_spouse_earned
        # line 25 = min(line 22, line 23, line 24):
        # The smaller of the minimum earnings or dependent care benefits is used for the final calculation
        min_earned = min_(
            tax_unit("hi_dependent_care_benefits", period),
            tax_unit("hi_cdcc_min_head_spouse_earned", period),
        )
        # line 26:
        agi = tax_unit("hi_agi", period)
        # line 27:
        rate = p.rate.calc(agi, right=True)
        # return: line 28 = line 27 * line 25:
        return rate * min_earned
