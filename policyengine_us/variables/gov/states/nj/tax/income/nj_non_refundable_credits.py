from policyengine_us.model_api import *


class nj_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula_2018(tax_unit, period, parameters):
        return tax_unit("nj_cdcc", period)

    def formula_2021(tax_unit, period, parameters):
        return 0
