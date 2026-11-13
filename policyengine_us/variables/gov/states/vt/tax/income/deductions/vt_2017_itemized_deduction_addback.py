from policyengine_us.model_api import *


class vt_2017_itemized_deduction_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont 2017 itemized deduction addback"
    unit = USD
    documentation = (
        "Federal itemized deductions Vermont adds back to 2017 federal "
        "taxable income, following Schedule IN-155: deducted state and local "
        "income taxes, up to the itemized deductions above the federal "
        "standard deduction, plus other itemized deductions (excluding "
        "medical and charitable) above 2.5 times the federal standard "
        "deduction. Itemized deductions include wagering losses and are after "
        "the section 68 limitation, which also scales the income taxes and "
        "charity."
    )
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        # Former 32 V.S.A. § 5811(21)(A)(iii)-(iv), reproduced in 2017 Vt.
        # Acts No. 73, § 13a. PDF pages 21-22.
        "https://legislature.vermont.gov/Documents/2018/Docs/ACTS/ACT073/ACT073%20As%20Enacted.pdf#page=21",
        # 2017 Schedule IN-155 and the Department's 2017 worksheet for limited
        # itemized deductions.
        "https://web.archive.org/web/20250629013817/https://tax.vermont.gov/sites/tax/files/documents/IN-155-2017.pdf",
        "https://web.archive.org/web/20201019064237/https://tax.vermont.gov/sites/tax/files/documents/2017%20IN-155%20Worksheet.xlsx",
    )

    def formula_2017(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.deductions.itemized_addback
        itemizes = tax_unit("tax_unit_itemizes", period)
        # IN-155 line 1 takes Schedule A line 29: allowed itemized deductions
        # after the section 68 limitation, including wagering losses, which
        # itemized_taxable_income_deductions leaves out.
        itemized = add(
            tax_unit,
            period,
            ["itemized_taxable_income_deductions", "wagering_losses_deduction"],
        )
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
        # The Department's worksheet for limited itemized deductions scales
        # income taxes and charity by the share of the limited deductions that
        # section 68 leaves. Section 68(c) doesn't limit medical expenses.
        limitation = parameters(period).gov.irs.deductions.itemized.limitation
        total = tax_unit("total_itemized_taxable_income_deductions", period)
        excluded = add(tax_unit, period, limitation.excluded_deductions)
        limited = max_(total - excluded, 0)
        reduction = tax_unit("itemized_taxable_income_deductions_reduction", period)
        remaining_share = 1 - np.divide(
            reduction, limited, out=np.zeros_like(limited), where=limited > 0
        )
        allowed_income_taxes = deducted_income_taxes * remaining_share
        allowed_charitable = tax_unit("charitable_deduction", period) * remaining_share
        medical = tax_unit("medical_expense_deduction", period)
        income_tax_addback = min_(allowed_income_taxes, max_(itemized - standard, 0))
        other_deductions = (
            itemized - allowed_income_taxes - medical - allowed_charitable
        )
        other_addback = max_(other_deductions - p.other_multiple * standard, 0)
        return where(itemizes, income_tax_addback + other_addback, 0)

    def formula_2018(tax_unit, period, parameters):
        return 0
