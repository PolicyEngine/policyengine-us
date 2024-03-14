from policyengine_us.model_api import *


class disabled_tax_unit_head_or_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Head or Spouse of tax unit is disabled"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        disabled_person = person("is_disabled", period)
        return tax_unit.any(disabled_person & is_head_or_spouse)
