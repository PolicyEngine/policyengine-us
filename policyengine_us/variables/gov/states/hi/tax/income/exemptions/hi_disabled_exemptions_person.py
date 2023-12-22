from policyengine_us.model_api import *


class hi_disabled_exemptions_person(Variable):
    value_type = float
    entity = Person
    label = "Hawaii disabled exemptions for each person"
    unit = USD
    documentation = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    definition_period = YEAR
    defined_for = "hi_disabled_exemptions_eligible_person"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.exemptions
        disabled = person("is_disabled", period)
        aged = person("age", period) >= p.aged_threshold
        return max_(disabled * p.disabled, p.base * (1 + aged))
