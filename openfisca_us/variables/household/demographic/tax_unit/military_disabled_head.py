from openfisca_us.model_api import *


class military_disabled_head(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit head is legally disabled as a result of military service"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        military_disabled = person(
            "is_fully_disabled_service_connected_veteran", period
        )
        head = person("is_tax_unit_head", period)
        return tax_unit.any(military_disabled & head)
