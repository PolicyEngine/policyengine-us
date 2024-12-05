from policyengine_us.model_api import *


class middle_rate_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Middle rate tax"  # DWKS29
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
        # Schedule D Tax Worksheet line 24
        filing_status = tax_unit("filing_status", period)
        capital_gains = parameters(period).gov.irs.capital_gains.brackets
        computed_gains_after_1250_and_28_percent_rate_gains = tax_unit(
            "computed_gains_after_1250_and_28_percent_rate_gains", period
        )  # dwks13
        # Schedule D Tax Worksheet line 20 for 2017 and 2018, or line 22 for years after
        capital_gains_taxable_difference_after_gains_adjustments = tax_unit(
            "capital_gains_taxable_difference_after_gains_adjustments", period
        )
        # Schedule D Tax Worksheet line 21 for 2017 and 2018, or line 23 for years after
        minimum_of_taxable_income_and_adjusted_gains_after_special_rates_adjustments = min_(
            taxable_income, computed_gains_after_1250_and_28_percent_rate_gains
        )  # dwks21 = min_(dwks1, dwks13)
        # Schedule D Tax Worksheet line 22 for 2017 and 2018, or line 24 for years after
        capital_gains_taxable_difference_after_gains_adjustments_2 = capital_gains_taxable_difference_after_gains_adjustments  # dwks22 = dwks20
        # Schedule D Tax Worksheet line 23 for 2017 and 2018, or line 25 for years after
        adjusted_taxable_income_after_special_gains_and_threshold_deductions = max_(
            0,
            minimum_of_taxable_income_and_adjusted_gains_after_special_rates_adjustments
            - capital_gains_taxable_difference_after_gains_adjustments_2,
        )  # dwks23 = max_(0, dwks21 - dwks22)
        # Schedule D Tax Worksheet line 25 for 2017 and 2018, or line 27 for years after
        min_capital_gains_and_taxable_income_2 = min_(
            capital_gains.thresholds["2"][filing_status], taxable_income
        )  # dwks25 = min_(capital_gains.thresholds["2"][filing_status], dwks1)
        computed_final_gains_after_all_adjustments = tax_unit(
            "computed_final_gains_after_all_adjustments", period
        )  # dwks19
        minimum_of_adjusted_gains_and_taxable_difference_after_gains_adjustments = min_(
            computed_final_gains_after_all_adjustments,
            capital_gains_taxable_difference_after_gains_adjustments,
        )  # dwks26 = min_(dwks19, dwks20)
        # Schedule D Tax Worksheet line 27 for 2017 and 2018, or line 29 for years after
        non_negative_adjusted_income_after_gains_and_taxable_difference_deductions = max_(
            0,
            min_capital_gains_and_taxable_income_2
            - minimum_of_adjusted_gains_and_taxable_difference_after_gains_adjustments,
        )  # dwks27 = max_(0, dwks25 - dwks26)
        # Schedule D Tax Worksheet line 28 for 2017 and 2018, or line 30 for years after
        dwks28 = min_(
            adjusted_taxable_income_after_special_gains_and_threshold_deductions,
            non_negative_adjusted_income_after_gains_and_taxable_difference_deductions,
        )  # dwks28 = min_(dwks23, dwks27)
        # Schedule D Tax Worksheet line 29 for 2017 and 2018, or line 31 for years after
        return (
            capital_gains.rates["2"] * dwks28
        )  # dwks29 = capital_gains.rates["2"] * dwks28
