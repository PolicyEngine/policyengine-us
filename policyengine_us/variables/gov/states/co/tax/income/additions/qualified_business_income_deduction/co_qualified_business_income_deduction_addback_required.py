from policyengine_us.model_api import *


class co_qualified_business_income_deduction_addback_required(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Required to add back the Colorado qualified business income deduction"
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-104 . Income tax imposed on individuals, estates, and trusts - section (3) (o)
        "https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-104-effective-until-official-proclamation-by-governor-income-tax-imposed-on-individuals-estates-and-trusts-single-rate-report-legislative-declaration-definitions-repeal",
        # C.R.S. 39-22-104(3)(o) Schedule F exception (Colorado Revised
        # Statutes 2025 official compilation, p. 383); addback continued
        # indefinitely by HB25B-1001 (2025 special session B), SECTION 2.
        "https://olls.info/crs/crs2025-title-39.pdf",
        "https://leg.colorado.gov/sites/default/files/2025b_1001_signed.pdf#page=1",
        # 2022 Colorado Individual Income Tax Filing Guide - Additions
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5",
        # 2021 Colorado Individual Income Tax Filing Guide - Additions
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2021.pdf#page=5",
        # Individual Income Tax Guide - Part 3 Additions to Taxable Income
        "https://tax.colorado.gov/individual-income-tax-guide",
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(
            period
        ).gov.states.co.tax.income.additions.qualified_business_income_deduction
        above_agi_threshold = agi > p.agi_threshold[filing_status]
        # C.R.S. 39-22-104(3)(o): the addback does not apply to a taxpayer who
        # is required to file a Schedule F (Profit or Loss From Farming), or
        # successor form, with the federal return for the tax year in which the
        # section 199A deduction is claimed.
        files_schedule_f = tax_unit("tax_unit_files_schedule_f", period)
        return above_agi_threshold & ~files_schedule_f
