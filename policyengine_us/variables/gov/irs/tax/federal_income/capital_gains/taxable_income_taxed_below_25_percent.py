from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.before_credits.tax_at_main_rates import (
    amount_taxed_below_rate,
)


class taxable_income_taxed_below_25_percent(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable income taxed at a rate below 25 percent"
    unit = USD
    documentation = (
        "The amount of taxable income that the regular rate schedule taxes at "
        "a rate below 25 percent: under the 10, 12, 22, 24, 32, 35 and 37 "
        "percent schedule, taxable income up to the top of the 24 percent "
        "bracket. Section 1(h)(1)(A) taxes capital gain at the regular rates "
        "up to this amount, or taxable income less adjusted net capital gain "
        "if less. Schedule D Tax Worksheet line 19. For a taxpayer excluding "
        "foreign earned income, taxable income includes the excluded amount."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(1)(A)(ii)(I)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_1_A_ii_I",
        ),
        dict(
            title="26 U.S. Code § 911(f)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Schedule D Tax Worksheet, line 19",
            href="https://www.irs.gov/pub/irs-pdf/i1040sd.pdf#page=15",
        ),
    ]

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs
        # Worksheet line 1: taxable income, or for a Form 2555 filer line 3
        # of the Foreign Earned Income Tax Worksheet (26 U.S.C. 911(f)).
        taxable_income = tax_unit("taxable_income_plus_section_911_exclusion", period)
        filing_status = tax_unit("filing_status", period)
        return amount_taxed_below_rate(
            taxable_income,
            filing_status,
            p.income.bracket,
            p.capital_gains.regular_rate_limit,
        )
