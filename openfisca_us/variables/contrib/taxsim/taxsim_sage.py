from openfisca_us.model_api import *


class taxsim_sage(Variable):
    value_type = int
    entity = TaxUnit
    label = "Age of spouse"
    unit = "year"
    documentation = "Age of spouse (zero if unknown or not a joint return). It is an error to specify a non-zero spouse age for an unmarried taxpayer."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_head = person("is_tax_unit_spouse", period)
        age = person("age", period)
        return tax_unit.sum(age * is_head)
