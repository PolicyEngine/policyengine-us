from policyengine_us.model_api import *


class head_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Head's adjusted earnings"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        adjusted_earnings = person("adjusted_earnings", period)
        is_head = person("is_tax_unit_head", period)
        return tax_unit.sum(is_head * adjusted_earnings)
