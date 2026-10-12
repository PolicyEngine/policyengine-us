from policyengine_us.model_api import *


class regular_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Regular tax before credits"
    documentation = (
        "The regular tax on all taxable income, qualified dividends and "
        "capital gains included, before credits: the tax at the main rates "
        "plus the capital gains tax, which income_tax_before_credits also "
        "adds. Schedule D Tax Worksheet line 47 (or Qualified Dividends and "
        "Capital Gain Tax Worksheet line 25, or the Tax Table or Tax "
        "Computation Worksheet without dividends or gains); for a Form 2555 "
        "filer, line 6 of the Foreign Earned Income Tax Worksheet. Form 6251 "
        "line 10 starts from it."
    )
    unit = USD
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(1)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_1",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Schedule D Tax Worksheet, line 47",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=16",
        ),
        dict(
            title="2025 Form 6251, line 10",
            href="https://www.irs.gov/pub/irs-prior/f6251--2025.pdf#page=1",
        ),
    ]
    adds = ["income_tax_main_rates", "capital_gains_tax"]
