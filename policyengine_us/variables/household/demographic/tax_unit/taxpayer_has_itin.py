from policyengine_us.model_api import *


class taxpayer_has_itin(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit head or spouse has ITIN"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_itin = person("has_itin", period)
        return tax_unit.any(head_or_spouse & has_itin)
