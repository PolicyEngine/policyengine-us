from policyengine_us.model_api import *


class min_head_spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Less of head and spouse's earnings"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        is_joint = tax_unit("tax_unit_is_joint", period)
        head_earnings = tax_unit("head_earned", period)
        spouse_earnings = tax_unit("spouse_earned", period)
        return where(
            is_joint,
            min_(head_earnings, spouse_earnings),
            head_earnings,
        )
