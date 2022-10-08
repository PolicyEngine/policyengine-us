from openfisca_us.model_api import *


class ca_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "CalEITC amount"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/file/personal/credits/california-earned-income-tax-credit.html#What-you-ll-get"
    defined_for = "ca_eitc_eligible"

    def formula(tax_unit, period, parameters):
        # Phase-in until the phase-in earned income amount.
        p = parameters(period).gov.states.ca.tax.income.credits.earned_income
        adj_federal_eitc = tax_unit("ca_federal_eitc", period)
        qualifying_children = add(
            tax_unit, period, ["ca_is_qualifying_child_for_caleitc"]
        )
        # TODO: Find out how it phases in.
        earned_income = tax_unit("tax_unit_earned_income", period)
        is_in_phase_in_range = earned_income <= p.phase_in_end.calc(
            qualifying_children
        )
        # Phase-out until the intra-phase-out kink.
        phase_out_kink_amount = p.phase_out_kink_amount.calc(
            qualifying_children
        )
        # TODO
        is_in_first_phase_out_range = False
        first_phase_out_range_amount = 0
        # Phase-out beyond the kink to the maximum earnings.
        # max_earnings
        # TODO
        second_phase_out_amount = 0
        # Also check eligib
        return select(
            [is_in_phase_in_range, is_in_first_phase_out_range],
            [
                adj_federal_eitc * p.adjustment_factor,
                first_phase_out_range_amount,
            ],
            second_phase_out_amount,
        )
