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
        exemptions = tax_unit("exemptions_count", period)
        p = parameters(period).gov.states.hi.tax.income.exemptions
        # Aged heads and spouses get an extra base exemption.
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        aged = person("age", period) >= p.aged_threshold
        aged_head_or_spouse = tax_unit.sum(aged & head_or_spouse)
        total_exemptions_including_aged = exemptions + aged_head_or_spouse
        return total_exemptions_including_aged * p.base
