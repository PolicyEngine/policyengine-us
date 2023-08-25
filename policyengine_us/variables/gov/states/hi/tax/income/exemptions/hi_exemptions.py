from policyengine_us.model_api import *


class hi_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii exemptions"
    unit = USD
    documentation = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.exemptions
        
        num_exemp = tax_unit("exemptions", period)
        disabled_head = tax_unit("disabled_head", period)
        disabled_spouse = tax_unit("disabled_spouse", period)
        aged_spouse = tax_unit("age_spouse", period)
        
        return where(
            disabled_head,
            where(
                disabled_spouse,
                p.disability_exemptions.disabled_spouse,
                where(
                    aged_spouse,
                    p.disability_exemptions.aged_and_undisabled_spouse,
                    p.disability_exemptions.unaged_undisabled_spouse
                )
            ),
            p.regular_exemptions * num_exemp
        )