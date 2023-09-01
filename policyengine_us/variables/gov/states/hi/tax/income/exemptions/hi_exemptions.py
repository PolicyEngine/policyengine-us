from policyengine_us.model_api import *


class hi_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii exemptions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.exemptions

        person = tax_unit.members

        exemp = tax_unit("exemptions", period)
        
        disabled_head = tax_unit("head_is_disabled", period).astype(int)

        disabled_spouse = tax_unit("spouse_is_disabled", period).astype(int)

        aged_head = person("age_head", period) >= p.age_theshold.astype(int)

        aged_spouse = person("age_spouse", period) >= p.age_theshold.astype(int)

        head_total_exemptions = where(disabled_head == 1, exemp - disabled_head, exemp +  aged_head)

        spouse_total_exemptions = where(disabled_spouse == 1, exemp - disabled_spouse, exemp +  aged_spouse)

        exemption_base_amount = (head_total_exemptions + spouse_total_exemptions) * p.base

        disabled_exemptions = (disabled_head + disabled_spouse) * p.disabled


        return exemption_base_amount + disabled_exemptions
        