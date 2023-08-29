from policyengine_us.model_api import *


class ga_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        agi = tax_unit("ga_agi", period)
        deductions = tax_unit("ga_deductions", period)
        exemptions = tax_unit("ga_exemptions", period)
        return max_(0, agi - deductions - exemptions)
