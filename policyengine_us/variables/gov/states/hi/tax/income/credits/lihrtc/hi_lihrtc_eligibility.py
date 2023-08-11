from policyengine_us.model_api import *


class hi_lihr_eligible(Variable):
    value_type = bool 
    entity = TaxUnit
    label = "Hawaii lihrtc eligible"
    definition_period = YEAR
    reference = " https://files.hawaii.gov/tax/legal/har/har_235.pdf"  # page: 105 §18-235-55.7 (b)
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.hi.tax.income.credits.lihrtc

        agi = taxunit("hi_agi",period) # or agi = taxunit("adjusted_gross_income",period)
        rent_pay = person("rent",period)

        rent_eligible = (
            rent_pay > p.rent_threshold
        )

        agi_eligible = (
            agi < p.agi_threshold
        )
        
        return agi_eligible & rent_eligible
