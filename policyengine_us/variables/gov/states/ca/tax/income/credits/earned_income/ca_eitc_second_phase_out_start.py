from policyengine_us.model_api import *


class ca_eitc_second_phase_out_start(Variable):
    value_type = float
    entity = TaxUnit
    label = "CalEITC second phase-out start"
    unit = USD
    documentation = "California begins secondarily phasing out the CalEITC at this earnings level."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        maximum = tax_unit("ca_eitc_maximum", period)
        ca_eitc = parameters(
            period
        ).gov.states.ca.tax.income.credits.earned_income
        count_children = tax_unit("eitc_child_count", period)
        # Apply the adjustment factor to the phase-out rate.
        phase_out_rate = (
            ca_eitc.phase_out.rate.calc(count_children)
            * ca_eitc.adjustment.factor
        )
        # Multiply and divide the second phase-out start by the adjustment factors.
        eitc_at_which_second_phase_out_starts = (
            ca_eitc.phase_out.final.start.calc(count_children)
            * ca_eitc.adjustment.factor
            / ca_eitc.adjustment.divisor
        )
        eitc_difference = maximum - eitc_at_which_second_phase_out_starts
        earnings_to_cover_eitc_difference = eitc_difference / phase_out_rate
        return (
            earnings_to_cover_eitc_difference
            + ca_eitc.phase_out.start.calc(count_children)
        )
