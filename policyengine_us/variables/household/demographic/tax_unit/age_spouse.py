from policyengine_us.model_api import *


class age_spouse(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Age of spouse of tax unit"
    documentation = "Age in years of spouse (i.e. secondary adult if present)"
    unit = "year"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        spouse = person("is_tax_unit_spouse", period)
        return tax_unit.max(age * spouse)
