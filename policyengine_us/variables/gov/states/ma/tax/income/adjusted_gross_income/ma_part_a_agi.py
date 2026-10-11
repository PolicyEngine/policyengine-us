from policyengine_us.model_api import *


class ma_part_a_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2"  # (c)
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        part_a_gross_income = tax_unit("ma_part_a_gross_income", period)
        short_term_capital_gains = add(tax_unit, period, ["short_term_capital_gains"])
        nonnegative_short_term_capital_gains = max_(0, short_term_capital_gains)
        # Massachusetts Schedule D, line 13 includes capital gain
        # distributions reported without a federal Schedule D (line 6).
        long_term_capital_gains = add(
            tax_unit, period, ["long_term_capital_gains", "non_sch_d_capital_gains"]
        )
        long_term_capital_loss = max_(0, -long_term_capital_gains)

        long_term_loss_against_short_term_gain = min_(
            long_term_capital_loss,
            nonnegative_short_term_capital_gains,
        )
        # Schedule B, lines 20 and 32.
        losses_against_dividends = add(
            tax_unit,
            period,
            [
                "ma_short_term_loss_against_dividends",
                "ma_long_term_loss_against_dividends",
            ],
        )

        tax = parameters(period).gov.states.ma.tax.income
        long_term_capital_gains_on_collectibles = add(
            tax_unit, period, ["long_term_capital_gains_on_collectibles"]
        )
        nonnegative_long_term_capital_gains_on_collectibles = max_(
            0, long_term_capital_gains_on_collectibles
        )
        long_term_gains_on_collectibles_deduction = (
            tax.capital_gains.long_term_collectibles_deduction
            * nonnegative_long_term_capital_gains_on_collectibles
        )

        deductions = (
            losses_against_dividends
            + long_term_loss_against_short_term_gain
            + long_term_gains_on_collectibles_deduction
        )
        return max_(0, part_a_gross_income - deductions)
