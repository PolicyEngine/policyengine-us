from policyengine_us.model_api import *


class hi_lihrtc_age_eligibility(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Age eligible for double the credit"
    definition_period = YEAR
    reference = " https://files.hawaii.gov/tax/legal/har/har_235.pdf#page=105"  #§18-235-55.7 (b)

    def formula(person, period, parameters):
        person = tax_unit.members
        age = person("age",period)
        p = parameters(period).gov.states.hi.tax.income.credits.lihrtc

        age_eligible = (
            age >= p.age_threshold
        )
        return age_eligible