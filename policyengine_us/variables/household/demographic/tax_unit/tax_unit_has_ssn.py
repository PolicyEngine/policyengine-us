from policyengine_us.model_api import *


class tax_unit_has_ssn(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "All members in the tax unit have ssn"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        has_ssn = person("has_ssn", period)
        # All members need to have ssn, including child
        return tax_unit.all(has_ssn)
