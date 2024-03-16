from policyengine_us.model_api import *


class tax_unit_married(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit is married"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        return tax_unit.any(person("is_tax_unit_spouse", period))
