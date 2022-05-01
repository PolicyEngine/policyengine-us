from openfisca_us.model_api import *


class blind_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit spouse is blind"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        blind = person("is_blind", period)
        spouse = person("is_tax_unit_spouse", period)
        return tax_unit.any(blind & spouse)
