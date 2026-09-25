from policyengine_us.model_api import *


class ca_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "CalEITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2023/2023-3514-instructions.html",  # California Earned Income Tax Credit Worksheet
        "https://www.ftb.ca.gov/forms/2024/2024-3514-booklet.html",
        "https://www.ftb.ca.gov/forms/2025/2025-3514-booklet.html",
    )
    defined_for = "ca_eitc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.earned_income

        child_count = tax_unit("eitc_child_count", period)

        phase_in_rate = p.phase_in.rate.calc(child_count) * p.adjustment.factor
        phase_in_max_income = p.earned_income_amount.calc(child_count)

        phase_out_min_income = p.phase_out.start.calc(child_count)
        phase_out_rate = p.phase_out.rate.calc(child_count) * p.adjustment.factor

        second_phase_out_start_eitc = p.phase_out.final.start.calc(
            child_count
        )  # Expressed as the EITC amount at which the second phase-out starts,
        # not the income level.

        maximum_eitc = phase_in_max_income * phase_in_rate
        eitc_fall_by_first_phase_out = maximum_eitc - second_phase_out_start_eitc
        earnings_range_of_first_phase_out = (
            eitc_fall_by_first_phase_out / phase_out_rate
        )
        second_phase_out_start = (
            phase_out_min_income + earnings_range_of_first_phase_out
        )
        second_phase_out_end = p.phase_out.final.end

        def credit_for(income):
            phase_in_income = min_(income, phase_in_max_income)
            phased_in_amount = phase_in_income * phase_in_rate

            phase_out_income = max_(0, income - phase_out_min_income)
            phase_out_income = min_(phase_out_income, earnings_range_of_first_phase_out)
            amount_after_first_phase_out = (
                phased_in_amount - phase_out_income * phase_out_rate
            )
            percentage_along_second_phase_out = min_(
                (income - second_phase_out_start)
                / (second_phase_out_end - second_phase_out_start),
                1,
            )
            return where(
                income > second_phase_out_start,
                amount_after_first_phase_out * (1 - percentage_along_second_phase_out),
                amount_after_first_phase_out,
            )

        earned_income = tax_unit("filer_adjusted_earnings", period)
        agi = tax_unit("adjusted_gross_income", period)
        # The California Earned Income Tax Credit Worksheet (FTB 3514
        # instructions) figures the credit on California earned income (line 2)
        # and on federal AGI (line 5) and takes the smaller (line 6) -- the same
        # earned-income/AGI comparison the federal EITC uses. Per RTC 17052(a)
        # / IRC 32(a)(2)(B), the AGI branch uses "adjusted gross income (or, if
        # greater, the earned income)", so the AGI lookup runs on the greater of
        # federal AGI and earned income (mirroring federal eitc_reduction). When
        # AGI <= earnings this makes the min_ a no-op (worksheet line 5 blank).
        higher_income = max_(earned_income, agi)
        return min_(credit_for(earned_income), credit_for(higher_income))
