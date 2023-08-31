from policyengine_us.model_api import *


class co_federal_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal taxable income for Colorado tax purposes"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    # Colorado used fedral taxable income as a starting point for calculating
    # personal income taxes as possosed to federal adjusted gross income.
    # Due to a cricluar reference the federal taxable income is replicated with
    # itemized deductions less SALT deduction.
    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        itemizes = itemizes = tax_unit("tax_unit_itemizes", period)
        deductions_if_itemizing = tax_unit(
            "itemized_deductions_less_salt", period
        )
        deductions_if_not_itemizing = tax_unit(
            "taxable_income_deductions_if_not_itemizing", period
        )
        deductions = where(
            itemizes, deductions_if_itemizing, deductions_if_not_itemizing
        )
        return max_(0, agi - deductions)
