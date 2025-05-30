from policyengine_us.model_api import *


class ca_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "CalEITC"
    unit = USD
    definition_period = YEAR
    defined_for = "ca_eitc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.earned_income

        earned_income = tax_unit("filer_adjusted_earnings", period)
        child_count = tax_unit("eitc_child_count", period)

        phase_in_rate = p.phase_in.rate.calc(child_count) * p.adjustment.factor
        phase_in_max_income = p.earned_income_amount.calc(child_count)

        phase_in_income = min_(earned_income, phase_in_max_income)
        phased_in_amount = phase_in_income * phase_in_rate

        phase_out_min_income = p.phase_out.start.calc(child_count)
        phase_out_rate = (
            p.phase_out.rate.calc(child_count) * p.adjustment.factor
        )

        phase_out_income = max_(0, earned_income - phase_out_min_income)

        second_phase_out_start_eitc = p.phase_out.final.start.calc(
            child_count
        )  # Expressed as the EITC amount at which the second phase-out starts,
        # not the income level.

        maximum_eitc = phase_in_max_income * phase_in_rate
        eitc_fall_by_first_phase_out = (
            maximum_eitc - second_phase_out_start_eitc
        )
        earnings_range_of_first_phase_out = (
            eitc_fall_by_first_phase_out / phase_out_rate
        )
        second_phase_out_start = (
            phase_out_min_income + earnings_range_of_first_phase_out
        )
        second_phase_out_end = p.phase_out.final.end

        phase_out_income = min_(
            phase_out_income, earnings_range_of_first_phase_out
        )
        amount_after_first_phase_out = (
            phased_in_amount - phase_out_income * phase_out_rate
        )
        percentage_along_second_phase_out = min_(
            (earned_income - second_phase_out_start)
            / (second_phase_out_end - second_phase_out_start),
            1,
        )
        return where(
            earned_income > second_phase_out_start,
            amount_after_first_phase_out
            * (1 - percentage_along_second_phase_out),
            amount_after_first_phase_out,
        )
