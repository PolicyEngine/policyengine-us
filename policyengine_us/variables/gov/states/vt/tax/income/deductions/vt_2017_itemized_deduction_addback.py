from policyengine_us.model_api import *


class vt_2017_itemized_deduction_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont 2017 itemized deduction addback"
    unit = USD
    documentation = (
        "Federal itemized deductions Vermont adds back to 2017 federal "
        "taxable income: deducted state and local income taxes, up to the "
        "itemized deductions above the federal standard deduction, plus other "
        "itemized deductions (excluding medical and charitable) above 2.5 "
        "times the federal standard deduction."
    )
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        # Former 32 V.S.A. § 5811(21)(A)(iii)-(iv), reproduced in 2017 Vt.
        # Acts No. 73, § 13a. PDF pages 21-22.
        "https://legislature.vermont.gov/Documents/2018/Docs/ACTS/ACT073/ACT073%20As%20Enacted.pdf#page=21",
    )

    def formula_2017(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.deductions.itemized_addback
        itemizes = tax_unit("tax_unit_itemizes", period)
        # Allowed federal itemized deductions, after the section 68 limitation.
        itemized = tax_unit("itemized_taxable_income_deductions", period)
        standard = tax_unit("standard_deduction", period)
        # The SALT deduction holds income taxes only when they exceed sales
        # taxes (state_and_local_sales_or_income_tax takes the larger).
        income_taxes = add(
            tax_unit, period, ["state_withheld_income_tax", "local_income_tax"]
        )
        sales_taxes = add(tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        salt = tax_unit("salt_deduction", period)
        deducted_income_taxes = where(
            income_taxes >= sales_taxes, min_(income_taxes, salt), 0
        )
        income_tax_addback = min_(deducted_income_taxes, max_(itemized - standard, 0))
        medical = tax_unit("medical_expense_deduction", period)
        charitable = tax_unit("charitable_deduction", period)
        other_deductions = itemized - deducted_income_taxes - medical - charitable
        other_addback = max_(other_deductions - p.other_multiple * standard, 0)
        return where(itemizes, income_tax_addback + other_addback, 0)

    def formula_2018(tax_unit, period, parameters):
        return 0
