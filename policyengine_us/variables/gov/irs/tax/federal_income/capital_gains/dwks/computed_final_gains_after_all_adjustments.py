from policyengine_us.model_api import *


class computed_final_gains_after_all_adjustments(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 6 of 6)"  # DWKS19
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f1040.pdf",
        "https://www.irs.gov/pub/irs-pdf/i1040gi.pdf",
        "https://www.irs.gov/pub/irs-pdf/f1040sd.pdf",
    )

    def formula(tax_unit, period, parameters):
        taxable_income_minus_gains = tax_unit(
            "taxable_income_minus_gains", period
        )  # dwks14
        capital_gains = parameters(period).gov.irs.capital_gains.brackets
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("taxable_income", period)  # dwks1
        min_capital_gains_and_taxable_income = min_(
            capital_gains.thresholds["1"][filing_status], taxable_income
        )  # dwks16
        min_capital_gains_and_taxable_income_and_taxable_income_minus_gains = (
            min_(
                taxable_income_minus_gains,
                min_capital_gains_and_taxable_income,
            )
        )  # dwks17
        computed_dividends_gains_whether_has_gains = tax_unit(
            "computed_dividends_gains_whether_has_gains", period
        )  # dwks10
        taxable_income_minus_computed_dividends_gains_whether_has_gains = max_(
            0, taxable_income - computed_dividends_gains_whether_has_gains
        )  # dwks18
        return max_(
            min_capital_gains_and_taxable_income_and_taxable_income_minus_gains,
            taxable_income_minus_computed_dividends_gains_whether_has_gains,
        ) * tax_unit("has_qdiv_or_ltcg", period)
