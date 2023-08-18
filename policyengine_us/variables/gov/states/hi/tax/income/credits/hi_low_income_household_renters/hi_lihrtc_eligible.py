from policyengine_us.model_api import *


class hi_lihrtc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Hawaii low income household renters tax credit"
    definition_period = YEAR
    reference = " https://files.hawaii.gov/tax/legal/har/har_235.pdf#page=105"  # §18-235-55.7 (b)
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.lihrtc

        agi = tax_unit("adjusted_gross_income", period)
        rents = tax_unit("rents", period)

        return (rents > p.threshold.rent) & (agi < p.threshold.agi)
