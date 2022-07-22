from openfisca_us.model_api import *


class ma_part_a_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2"  # (c)
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        part_a_gross_income = tax_unit("ma_part_a_gross_income", period)
        short_term_capital_gains = add(
            tax_unit, period, ["short_term_capital_gains"]
        )
        short_term_capital_loss = max_(0, -short_term_capital_gains)
        nonnegative_short_term_capital_gains = max_(
            0, short_term_capital_gains
        )
        interest_and_dividends = (
            part_a_gross_income - nonnegative_short_term_capital_gains
        )

        tax = parameters(period).gov.states.ma.tax.income
        interest_dividends_deduction_cap = (
            tax.capital_gains.deductible_against_interest_dividends
        )
        short_term_loss_against_interest_dividends = min_(
            interest_dividends_deduction_cap,
            min_(
                interest_and_dividends,
                short_term_capital_loss,
            ),
        )

        long_term_capital_gains = add(
            tax_unit, period, ["long_term_capital_gains"]
        )
        long_term_capital_loss = max_(0, -long_term_capital_gains)
        nonnegative_long_term_capital_gains = max_(0, long_term_capital_gains)

        long_term_loss_against_short_term_gain = min_(
            long_term_capital_loss,
            nonnegative_short_term_capital_gains,
        )
        remaining_long_term_loss = (
            long_term_capital_loss - long_term_loss_against_short_term_gain
        )
        remaining_interest_dividends = (
            interest_and_dividends - short_term_loss_against_interest_dividends
        )
        remaining_interest_deduction_cap = (
            interest_dividends_deduction_cap
            - short_term_loss_against_interest_dividends
        )
        long_term_loss_against_interest_dividends = min_(
            remaining_interest_deduction_cap,
            min_(
                remaining_long_term_loss,
                remaining_interest_dividends,
            ),
        )

        long_term_gains_deduction = (
            tax.capital_gains.long_term_deduction
            * nonnegative_long_term_capital_gains
        )

        deductions = (
            short_term_loss_against_interest_dividends
            + long_term_loss_against_interest_dividends
            + long_term_loss_against_short_term_gain
            + long_term_gains_deduction
        )
        return max_(0, part_a_gross_income - deductions)
