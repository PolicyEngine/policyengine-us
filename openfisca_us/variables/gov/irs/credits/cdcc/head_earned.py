from openfisca_us.model_api import *


class head_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Head's earnings"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        earned_income = max_(0, person("earned", period))
        is_head = person("is_tax_unit_head", period)
        return tax_unit.sum(is_head * earned_income)
