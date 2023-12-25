from policyengine_us.model_api import *


class head_is_dependent_elsewhere(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Is tax-unit head a dependent elsewhere"
    documentation = "Whether the filer for this tax unit is claimed as a dependent in another tax unit."

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        claimed_on_another_return = person(
            "claimed_as_dependent_on_another_return", period
        )
        is_head = person("is_tax_unit_head", period)
        return tax_unit.any(claimed_on_another_return & is_head)
