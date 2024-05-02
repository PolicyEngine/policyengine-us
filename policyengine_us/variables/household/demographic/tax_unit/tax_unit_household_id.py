from policyengine_us.model_api import *


class tax_unit_household_id(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit household ID"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        return tax_unit.value_from_first_person(
            person.household("household_id", period)
        )
