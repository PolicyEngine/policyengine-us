from policyengine_us.model_api import *


class regular_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Regular tax before credits"
    documentation = "Regular tax on regular taxable income before credits"
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
        capital_gains_taxable_difference_after_gains_adjustments = (
            min_capital_gains_and_taxable_income_1
            - min_capital_gains_and_taxable_income_and_taxable_income_minus_gains
        )  # dwks20 = dwks16 - dwks17
        lowest_rate_tax = (
            capital_gains.rates["1"]
            * capital_gains_taxable_difference_after_gains_adjustments
        )
        # Break in worksheet lines
        # Schedule D Tax Worksheet line 13
        computed_gains_after_1250_and_28_percent_rate_gains = tax_unit(
            "computed_gains_after_1250_and_28_percent_rate_gains", period
        )  # dwks13
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
        dwks29 = (
            capital_gains.rates["2"] * dwks28
        )  # dwks29 = capital_gains.rates["2"] * dwks28
        # Schedule D Tax Worksheet line 30 for 2017 and 2018, or line 32 for years after
        dwks30 = (
            capital_gains_taxable_difference_after_gains_adjustments_2 + dwks28
        )  # dwks30 = dwks22 + dwks28
        # Schedule D Tax Worksheet line 31 for 2017 and 2018, or line 33 for years after
        dwks31 = (
            minimum_of_taxable_income_and_adjusted_gains_after_special_rates_adjustments
            - dwks30
        )  # dwks31 = dwks21 - dwks30
        # Schedule D Tax Worksheet line 32 for 2017 and 2018, or line 34 for years after
        dwks32 = (
            capital_gains.rates["3"] * dwks31
        )  # dwks32 = capital_gains.rates["3"] * dwks31
        # Break in worksheet lines
        # Schedule D Tax Worksheet line 33 for 2017 and 2018, or line 35 for years after
        dwks33 = min_(
            tax_unit(
                "adjusted_capital_gains_reduced_by_investment_income", period
            ),  # dwks9
            add(
                tax_unit, period, ["unrecaptured_section_1250_gain"]
            ),  # Unrecaptured Section 1250 Gain Worksheet—Line 19
        )  # dwks33
        # Schedule D Tax Worksheet line 10
        dwks10 = tax_unit("dwks10", period)  # dwks10
        # Schedule D Tax Worksheet line 34 for 2017 and 2018, or line 36 for years after
        dwks34 = (
            dwks10 + computed_final_gains_after_all_adjustments
        )  # dwks34 = dwks10 + dwks19
        # Schedule D Tax Worksheet line 36 for 2017 and 2018, or line 38 for years after
        dwks36 = max_(0, dwks34 - dwks1)  # dwks36 = max_(0, dwks34 - dwks1)
        # Schedule D Tax Worksheet line 37 for 2017 and 2018, or line 39 for years after
        dwks37 = max_(0, dwks33 - dwks36)  # dwks37 = max_(0, dwks33 - dwks36)
        # Schedule D Tax Worksheet line 38 for 2017 and 2018, or line 40 for years after
        dwks38 = 0.25 * dwks37  # dwks38
        # Break in worksheet lines
        # Schedule D Tax Worksheet line 39 for 2017 and 2018, or line 41 for years after
        dwks39 = (
            computed_final_gains_after_all_adjustments
            + dwks20
            + dwks28
            + dwks31
            + dwks37
        )  # dwks39 = dwks19 + dwks20 + dwks28 + dwks31 + dwks37
        # Schedule D Tax Worksheet line 40 for 2017 and 2018, or line 42 for years after
        dwks40 = taxable_income - dwks39  # dwks40 = dwks1 - dwks39
        # Schedule D Tax Worksheet line 41 for 2017 and 2018, or line 43 for years after
        dwks41 = 0.28 * dwks40  # dwks41

        # Compute regular tax using bracket rates and thresholds
        reg_taxinc = max_(0, computed_final_gains_after_all_adjustments)
        p = parameters(period).gov.irs.income
        bracket_tops = p.bracket.thresholds
        bracket_rates = p.bracket.rates
        reg_tax = 0
        bracket_bottom = 0
        for i in range(1, len(list(bracket_rates.__iter__())) + 1):
            b = str(i)
            bracket_top = bracket_tops[b][filing_status]
            reg_tax += bracket_rates[b] * amount_between(
                reg_taxinc, bracket_bottom, bracket_top
            )
            bracket_bottom = bracket_top

        # Return to worksheet lines
        # Schedule D Tax Worksheet line 42 for 2017 and 2018, or line 44 for years after
        dwks42 = reg_tax  # dwks 42
        # Schedule D Tax Worksheet line 43 for 2017 and 2018, or line 45 for years after
        dwks43 = sum(
            [
                dwks29,
                dwks32,
                dwks38,
                dwks41,
                dwks42,
                lowest_rate_tax,
            ]
        )  # dwks43
        # Schedule D Tax Worksheet line 44 for 2017 and 2018, or line 46 for years after
        income_tax_main_rates = tax_unit(
            "income_tax_main_rates", period
        )  # dwks44
        # Schedule D Tax Worksheet line 45 for 2017 and 2018, or line 47 for years after
        dwks45 = min_(
            dwks43, income_tax_main_rates
        )  # dwks45 = min_(dwks43, dwks44)
        hasqdivltcg = tax_unit("hasqdivltcg", period)
        return where(hasqdivltcg, dwks45, income_tax_main_rates)


taxbc = variable_alias("taxbc", regular_tax_before_credits)
