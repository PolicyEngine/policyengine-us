from policyengine_us.model_api import *


class hi_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii CDCC"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=40"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.cdcc
        # line 22
        dcb = tax_unit("hi_dcb", period)
        # line 23,24
        min_head_spouse_earned = tax_unit("min_head_spouse_earned", period)
        # line 25
        min_amount = min_(dcb, min_head_spouse_earned)
        # line 26
        agi = tax_unit("adjusted_gross_income", period)
        rate = p.rates.calc(agi)

        return rate * min_amount
