from policyengine_us.model_api import *


class hi_disabled_exemptions_eligible_person(Variable):
    value_type = float
    entity = Person
    label = "Eligible person for the Hawaii disabled exemptions"
    unit = USD
    documentation = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        disabled = person("is_disabled", period)

        return head_or_spouse & disabled
