from policyengine_us.model_api import *


class hi_head_or_spouse_exemptions_person(Variable):
    value_type = float
    entity = Person
    label = "Hawaii exemptions amount for each head or spouse"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        p = parameters(period).gov.states.hi.tax.income.exemptions
        disabled = person("is_disabled", period)
        aged = person("age", period) >= p.aged_threshold
        # Filer can claim greater of the disabled or base exemption.
        disabled_exemption = disabled * p.disabled
        # Aged individuals get an extra base exemption.
        base_exemption = p.base * (1 + aged)
        return max_(disabled_exemption, base_exemption) * head_or_spouse
