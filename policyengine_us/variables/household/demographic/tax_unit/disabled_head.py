from policyengine_us.model_api import *


class disabled_head(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit head is legally disabled"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        disabled = person("is_ssi_disabled", period)
        head = person("is_tax_unit_head", period)
        return tax_unit.any(disabled & head)
