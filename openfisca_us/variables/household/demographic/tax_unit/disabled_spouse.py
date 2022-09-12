from openfisca_us.model_api import *


class disabled_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit spouse is legally disabled"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        disabled = person("is_ssi_disabled", period)
        spouse = person("is_tax_unit_spouse", period)
        return tax_unit.any(disabled & spouse)
