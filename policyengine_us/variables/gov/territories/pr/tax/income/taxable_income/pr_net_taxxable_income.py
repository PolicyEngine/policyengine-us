from policyengine_us.model_api import *


class pr_net_taxxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico net taxxable income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("pr_agi", period)
        exemptions = tax_unit("pr_exemptions", period)
        deductions = tax_unit("pr_deductions", period)
        return max_(0, agi - exemptions - deductions)
