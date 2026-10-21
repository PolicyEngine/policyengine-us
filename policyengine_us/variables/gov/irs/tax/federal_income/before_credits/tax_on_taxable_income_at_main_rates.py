from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.before_credits.tax_at_main_rates import (
    tax_at_main_rates,
)


class tax_on_taxable_income_at_main_rates(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax on all taxable income at the main rates"
    documentation = (
        "The tax on all taxable income, capital gains and qualified dividends "
        "included, at the ordinary rate schedule of 26 U.S.C. 1: Schedule D "
        "Tax Worksheet line 46 and Qualified Dividends and Capital Gain Tax "
        "Worksheet line 24. Section 1(h)(1) caps the regular tax at this "
        "amount. For a taxpayer excluding foreign earned income, taxable "
        "income includes the excluded amount and the tax on the excluded "
        "amount alone is subtracted, as in income_tax_main_rates."
    )
    unit = USD
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(1)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_1",
        ),
        dict(
            title="26 U.S. Code § 911(f)(1)(A)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f_1_A",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Schedule D Tax Worksheet, lines 46 and 47",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=16",
        ),
    ]

    def formula(tax_unit, period, parameters):
        # Worksheet line 1: taxable income, or for a Form 2555 filer line 3
        # of the Foreign Earned Income Tax Worksheet.
        taxable_income = tax_unit("taxable_income_plus_section_911_exclusion", period)
        bracket = parameters(period).gov.irs.income.bracket
        filing_status = tax_unit("filing_status", period)
        tax = tax_at_main_rates(max_(0, taxable_income), filing_status, bracket)
        # 26 U.S.C. 911(f)(1)(A): less the tax on the excluded amount alone
        # (Foreign Earned Income Tax Worksheet lines 5 and 6).
        excluded = max_(0, tax_unit("foreign_earned_income_exclusion", period))
        tax_on_excluded = tax_at_main_rates(excluded, filing_status, bracket)
        return where(excluded > 0, max_(0, tax - tax_on_excluded), tax)
