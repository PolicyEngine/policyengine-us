from policyengine_us.model_api import *


class military_disabled_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = (
        "Tax unit spouse is legally disabled as a result of military service"
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        military_disabled = person(
            "is_fully_disabled_service_connected_veteran", period
        )
        spouse = person("is_tax_unit_spouse", period)
        return tax_unit.any(military_disabled & spouse)
