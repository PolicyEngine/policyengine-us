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
        p = parameters(period).gov.states.hi.tax.income.exemptions
        # aged exemption
        aged_head = (tax_unit("age_head", period) >= p.aged_threshold).astype(
            int
        )
        aged_spouse = (
            tax_unit("age_spouse", period) >= p.aged_threshold
        ).astype(int)
        exemption_count = (
            tax_unit("exemptions_count", period) + aged_head + aged_spouse
        )
        return p.base * exemption_count
