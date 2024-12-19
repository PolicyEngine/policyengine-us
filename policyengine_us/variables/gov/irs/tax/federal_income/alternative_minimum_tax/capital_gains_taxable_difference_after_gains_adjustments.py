from policyengine_us.model_api import *


class capital_gains_taxable_difference_after_gains_adjustments(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = (
        "Capital gains taxable difference after gains adjustments"  # DWKS20
    )
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f1040sd.pdf",
        "https://www.irs.gov/pub/irs-prior/i1040sd--2017.pdf#page=15",
        "https://www.irs.gov/pub/irs-prior/i1040sd--2018.pdf#page=19",
        "https://www.irs.gov/pub/irs-prior/i1040sd--2023.pdf#page=16",
    )

    def formula(tax_unit, period, parameters):
        # Schedule D Tax Worksheet line 1
        taxable_income = tax_unit("taxable_income", period)  # dwks1
        # Schedule D Tax Worksheet line 15
        filing_status = tax_unit("filing_status", period)
        capital_gains = parameters(period).gov.irs.capital_gains.brackets
        # Schedule D Tax Worksheet line 16
        min_capital_gains_and_taxable_income_1 = min_(
            capital_gains.thresholds["1"][filing_status], taxable_income
        )  # dwks16
        # Schedule D Tax Worksheet line 17
        min_capital_gains_and_taxable_income_and_taxable_income_minus_gains = (
            min_(
                tax_unit("taxable_income_minus_gains", period),
                min_capital_gains_and_taxable_income_1,
            )
        )  # dwks17 = min_(tax_unit("dwks14", period), dwks16)
        # Schedule D Tax Worksheet line 20 for 2017 and 2018, or line 22 for years after
        return (
            min_capital_gains_and_taxable_income_1
            - min_capital_gains_and_taxable_income_and_taxable_income_minus_gains
        )  # dwks20 = dwks16 - dwks17
