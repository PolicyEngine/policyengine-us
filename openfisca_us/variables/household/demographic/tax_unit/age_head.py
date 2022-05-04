from openfisca_us.model_api import *


class age_head(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Age of head of tax unit"
    documentation = "Age in years of taxpayer (i.e. primary adult)"
    unit = "year"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        head = person("is_tax_unit_head", period)
        return tax_unit.max(age * head)
