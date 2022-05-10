from openfisca_us.model_api import *


class taxsim_pwages(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wages for primary taxpayer"
    unit = USD
    documentation = "Wage and salary income of Primary Taxpayer"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_primary = person("is_tax_unit_head", period)
        wages = person("employment_income", period)
        return tax_unit.sum(wages * is_primary)
