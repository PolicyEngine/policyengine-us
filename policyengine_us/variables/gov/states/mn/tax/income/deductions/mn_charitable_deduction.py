from policyengine_us.model_api import *


class mn_charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota charitable deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Charitable contributions allowable for Minnesota itemized deductions and the non-itemizer subtraction."
    reference = "https://www.revisor.mn.gov/statutes/cite/290.0122#stat.290.0122.4"
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        return tax_unit("charitable_deduction", period)

    def formula_2026(tax_unit, period, parameters):
        contributions = tax_unit("charitable_deduction_before_floor", period)
        contribution_base = tax_unit("positive_agi", period)
        p = parameters(period).gov.states.mn.tax.income.deductions.itemized.charity
        return max_(0, contributions - p.floor * contribution_base)
