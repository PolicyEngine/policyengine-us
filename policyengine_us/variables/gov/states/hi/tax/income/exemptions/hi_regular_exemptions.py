from policyengine_us.model_api import *


class hi_regular_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii regular exemptions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.hi.tax.income.exemptions
        # The total exemptions are reduced by the head and spouse as those are
        # calculated separately.
        head = tax_unit.any(person("is_tax_unit_head", period)).astype(int)
        spouse = tax_unit.any(person("is_tax_unit_spouse", period)).astype(int)

        exemption_count = tax_unit("exemptions_count", period) - head - spouse
        return p.base * exemption_count
