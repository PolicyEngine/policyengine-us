from openfisca_us.model_api import *


class blind_head(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit head is blind"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        blind = person("is_blind", period)
        head = person("is_tax_unit_head", period)
        return tax_unit.any(blind & head)
