from policyengine_us.model_api import *


class co_federal_deduction_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado federal deductions addback"
    unit = USD
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-104 . Income tax imposed on individuals, estates, and trusts - section (3)(p)
        "https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-104-effective-upon-official-proclamation-by-governor-income-tax-imposed-on-individuals-estates-and-trusts-single-rate-report-legislative-declaration-definitions-repeal",
        # 2022 Colorado Individual Income Tax Filing Guide - Additions - Line 4
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5",
        # Individual Income Tax Guide - Part 3 Additions to Taxable Income - Federal itemized or standard deductions
        "https://tax.colorado.gov/individual-income-tax-guide",
    )
    defined_for = "co_federal_deduction_addback_required"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.co.tax.income.additions.federal_deductions
        if p.itemized_only:
            deductions = tax_unit("itemized_taxable_income_deductions", period)
        else:
            deductions = tax_unit("taxable_income_deductions", period)
        filing_status = tax_unit("filing_status", period)
        exemption = p.exemption[filing_status]
        return max_(deductions - exemption, 0)
