from policyengine_us.model_api import *


class vt_2017_itemized_deduction_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont 2017 itemized deduction addback"
    unit = USD
    documentation = (
        "For 2017, Vermont filers add back deducted state and local income taxes, "
        "up to federal itemized deductions above the federal standard "
        "deduction. They also add back other itemized deductions, "
        "excluding medical and charitable deductions, above 2.5 times the "
        "standard deduction. PolicyEngine includes wagering losses in federal "
        "itemized deductions after applying section 68. Filers scale income "
        "taxes and charity by the share that section 68 leaves."
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
        # The filer enters allowed itemized deductions, including wagering losses,
        # after the section 68 limitation on IN-155 line 1 (Schedule A line 29).
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
        # Filers scale income taxes and charity by the share of limited
        # deductions that section 68 leaves, following the Department's worksheet.
        # Filers exclude medical expenses and wagering losses under section 68(c).
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
