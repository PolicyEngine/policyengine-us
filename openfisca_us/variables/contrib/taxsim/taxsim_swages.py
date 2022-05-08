from openfisca_us.model_api import *


class taxsim_swages(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wages for spouse"
    unit = USD
    documentation = "Wage and salary income of spouse"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_primary = person("is_tax_unit_spouse", period)
        wages = person("employment_income", period)
        return tax_unit.sum(wages * is_primary)
