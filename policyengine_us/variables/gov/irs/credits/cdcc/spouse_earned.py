from policyengine_us.model_api import *


class spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Spouse's adjusted earnings"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        adjusted_earnings = person("adjusted_earnings", period)
        is_spouse = person("is_tax_unit_spouse", period)
        return tax_unit.sum(is_spouse * adjusted_earnings)
