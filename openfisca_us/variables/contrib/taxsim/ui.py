from openfisca_us.model_api import *


class ui(Variable):
    value_type = float
    entity = TaxUnit
    label = "Unemployment insurance (spouse)"
    unit = USD
    documentation = "Unemployment compensation received - secondary taxpayer. The split is relevant only 2020-2021."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_spouse = person("is_tax_unit_spouse", period)
        unemployment_insurance = person("unemployment_insurance", period)
        return tax_unit.sum(unemployment_insurance * is_spouse)
