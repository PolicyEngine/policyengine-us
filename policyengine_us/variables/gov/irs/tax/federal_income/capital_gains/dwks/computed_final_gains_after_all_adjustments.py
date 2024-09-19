from policyengine_us.model_api import *


class computed_final_gains_after_all_adjustments(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 6 of 6)"  # DWKS19
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-prior/i1040sd--2017.pdf#page=16",
    )

    def formula(tax_unit, period, parameters):
        # Schedule D Tax Worksheet line 14
        taxable_income_minus_gains = tax_unit(
            "taxable_income_minus_gains", period
        )  # dwks14
        # Schedule D Tax Worksheet line 15
        capital_gains = parameters(period).gov.irs.capital_gains.brackets
        filing_status = tax_unit("filing_status", period)
        # Schedule D Tax Worksheet line 1
        taxable_income = tax_unit("taxable_income", period)  # dwks1
        # Schedule D Tax Worksheet line 16
        min_capital_gains_and_taxable_income = min_(
            capital_gains.thresholds["1"][filing_status], taxable_income
        )  # dwks16
        # Schedule D Tax Worksheet line 17
        min_capital_gains_and_taxable_income_and_taxable_income_minus_gains = (
            min_(
                taxable_income_minus_gains,
                min_capital_gains_and_taxable_income,
            )
        )  # dwks17
        # Schedule D Tax Worksheet line 10
        computed_dividends_gains_whether_has_gains = tax_unit(
            "computed_dividends_gains_whether_has_gains", period
        )  # dwks10
        # Schedule D Tax Worksheet line 18
        taxable_income_minus_computed_dividends_gains_whether_has_gains = max_(
            0, taxable_income - computed_dividends_gains_whether_has_gains
        )  # dwks18
        # Schedule D Tax Worksheet line 19
        return max_(
            min_capital_gains_and_taxable_income_and_taxable_income_minus_gains,
            taxable_income_minus_computed_dividends_gains_whether_has_gains,
        ) * tax_unit("has_qdiv_or_ltcg", period)
