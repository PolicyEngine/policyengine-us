from policyengine_us.model_api import *


class pell_grant_head_assets(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Pell Grant head assets"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        assets = person("pell_grant_countable_assets", period)
        is_parent = is_head | is_spouse
        return tax_unit.sum(is_parent * assets)
