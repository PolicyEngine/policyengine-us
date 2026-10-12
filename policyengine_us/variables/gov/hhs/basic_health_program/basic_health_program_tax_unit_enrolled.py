from policyengine_us.model_api import *


class basic_health_program_tax_unit_enrolled(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Tax unit has a Basic Health Program enrollee"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit.any(tax_unit.members("basic_health_program_enrolled", period))
