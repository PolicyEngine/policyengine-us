from policyengine_us.model_api import *


class nyc_school_tax_credit_rate_reduction_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC School Tax Credit Rate Reduction Amount"
    unit = USD
    definition_period = YEAR
    defined_for = "nyc_school_tax_credit_rate_reduction_amount_eligible"
    reference = (
        # NY Tax Law § 606(ggg)(4-b)
        "https://www.nysenate.gov/legislation/laws/TAX/606",
        # L.2017, ch. 59, Part C, § 2 (tables, PDF pages 8-9) and § 7
        # (applies to tax years beginning on and after January 1, 2017,
        # PDF page 14)
        "https://legislation.nysenate.gov/pdf/bills/2017/S2009C#page=8",
        "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=21",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.local.ny.nyc.tax.income.credits.school.rate_reduction.amount
        filing_status = tax_unit("filing_status", period)
        taxable_income = max_(tax_unit("nyc_taxable_income", period), 0)
        threshold = p.threshold[filing_status]
        # § 606(ggg)(4-b)(A)-(C): city taxable income not over the threshold
        # gets the first band rate; above it, the amount is a fixed base for
        # the filing status plus the excess rate on income over the threshold.
        first_band = p.first_band_rate * taxable_income
        above_threshold = p.base[filing_status] + p.excess_rate * (
            taxable_income - threshold
        )
        return where(taxable_income > threshold, above_threshold, first_band)
