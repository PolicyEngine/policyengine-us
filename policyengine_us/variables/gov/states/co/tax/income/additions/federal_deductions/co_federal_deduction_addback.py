from policyengine_us.model_api import *


class co_federal_deduction_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado federal deductions addback"
    unit = USD
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-104 . Income tax imposed on individuals, estates, and trusts - section (3)(p)
        "https://law.justia.com/codes/colorado/2023/title-39/specific-taxes/income-tax/article-22/part-1/section-39-22-104/",
        # C.R.S. 39-22-104(3)(p.5)(I) (2023-2025) and (3)(p.7)(I) (2026+),
        # Colorado Revised Statutes 2025 official compilation, pp. 382-384
        "https://olls.info/crs/crs2025-title-39.pdf",
        # 2022 Colorado Individual Income Tax Filing Guide - Additions - Line 4
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5",
        # Individual Income Tax Guide - Part 3 Additions to Taxable Income - Federal itemized or standard deductions
        "https://tax.colorado.gov/individual-income-tax-guide",
        # 1 CCR 201-2, Rule 39-22-104(3)(p)(3): coordination with other addbacks.
        "https://www.law.cornell.edu/regulations/colorado/39-22-104(3-parens-p)",
        # DR 0104 line 4 instructions, 2023 to 2025.
        "https://tax.colorado.gov/sites/tax/files/documents/Book0104_2023.pdf#page=6",
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104_book_2024.pdf#page=9",
        "https://tax.colorado.gov/sites/tax/files/documents/Book104_2025.pdf#page=9",
    )
    defined_for = "co_federal_deduction_addback_required"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.additions.federal_deductions
        if p.itemized_only:
            deductions = tax_unit("itemized_taxable_income_deductions", period)
        else:
            deductions = where(
                tax_unit("tax_unit_itemizes", period),
                tax_unit("itemized_taxable_income_deductions", period),
                tax_unit("standard_deduction", period),
            )
        filing_status = tax_unit("filing_status", period)
        exemption = p.exemption[filing_status]
        # Rule 39-22-104(3)(p)(3)(a)(i) reduces this addition by the state
        # income tax already added back under C.R.S. 39-22-104(3)(d)(I)
        # (DR 0104 line 2), but not by a share of state income tax deducted by a
        # partnership or S corporation, which co_state_addback does not include.
        state_income_tax_addback = tax_unit("co_state_addback", period)
        return max_(deductions - exemption - state_income_tax_addback, 0)
