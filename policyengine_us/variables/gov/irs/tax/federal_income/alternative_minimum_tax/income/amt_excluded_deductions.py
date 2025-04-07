from policyengine_us.model_api import *


class amt_excluded_deductions(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AMT taxable income excluded deductions"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/55#b_2"

    def formula(tax_unit, period, parameters):
        itemizing = tax_unit("tax_unit_itemizes", period)
        standard_deduction = tax_unit("standard_deduction", period)
        p = parameters(period).gov.irs.income.amt
        itemized_deductions_add_back = add(
            tax_unit, period, p.itemized_deductions_add_back
        )
        return where(
            itemizing, itemized_deductions_add_back, standard_deduction
        )
