from policyengine_us.model_api import *


class co_itemized_or_standard_deduction_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado itemized or standard deduction addback"
    unit = USD
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-104 . Income tax imposed on individuals, estates, and trusts - section (3)(p) - (p.5)
        "https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-104-effective-upon-official-proclamation-by-governor-income-tax-imposed-on-individuals-estates-and-trusts-single-rate-report-legislative-declaration-definitions-repeal",
        # 2022 Colorado Individual Income Tax Filing Guide - Additions - Line 4
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5",
        # Individual Income Tax Guide - Part 3 Additions to Taxable Income - Federal itemized or standard deductions
        "https://tax.colorado.gov/individual-income-tax-guide",
    )
    defined_for = "co_itemized_or_standard_deduction_addback_eligible"

    def formula_2022(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        p = parameters(
            period
        ).gov.states.co.tax.income.additions.itemized_or_standard_deduction_addback
        filing_status = tax_unit("filing_status", period)
        limit = p.limit[filing_status]
        federal_itemized_deduction = tax_unit(
            "itemized_taxable_income_deductions", period
        )
        exceeded_itemized_deduction = max_(
            federal_itemized_deduction - limit, 0
        )

        return exceeded_itemized_deduction * itemizes

    def formula_2023(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        federal_itemized_deduction = tax_unit(
            "itemized_taxable_income_deductions", period
        )
        federal_standard_deduction = tax_unit("standard_deduction", period)
        deduction = where(
            itemizes, federal_itemized_deduction, federal_standard_deduction
        )
        p = parameters(
            period
        ).gov.states.co.tax.income.additions.itemized_or_standard_deduction_addback
        filing_status = tax_unit("filing_status", period)
        limit = p.limit[filing_status]
        return max_(deduction - limit, 0)
