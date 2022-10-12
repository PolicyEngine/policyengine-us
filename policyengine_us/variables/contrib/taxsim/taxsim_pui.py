from policyengine_us.model_api import *


class taxsim_pui(Variable):
    value_type = float
    entity = TaxUnit
    label = "Unemployment compensation (primary taxpayer)"
    unit = USD
    documentation = "Unemployment Compensation received - primary taxpayer."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_primary = person("is_tax_unit_head", period)
        unemployment_compensation = person("unemployment_compensation", period)
        return tax_unit.sum(unemployment_compensation * is_primary)
