from policyengine_us.model_api import *


class ma_long_term_loss_against_dividends(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA long-term capital losses applied against dividends"
    documentation = (
        "Massachusetts Schedule B, line 32: long-term losses left after "
        "short-term gains, up to $2,000 of dividends less the short-term "
        "losses already applied in line 20."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # (c)(2)(b) and (c)(4)
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section2",
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2024/dor-2024-inc-sch-b-(form-1).pdf#page=2",
        "https://www.mass.gov/doc/2024-form-1-instructions/download#page=25",
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        short_term_capital_gains = add(tax_unit, period, ["short_term_capital_gains"])
        nonnegative_short_term_capital_gains = max_(0, short_term_capital_gains)
        long_term_capital_gains = add(tax_unit, period, ["long_term_capital_gains"])
        long_term_capital_loss = max_(0, -long_term_capital_gains)
        # Schedule B, line 25: long-term losses first offset short-term gains.
        remaining_long_term_loss = max_(
            0, long_term_capital_loss - nonnegative_short_term_capital_gains
        )
        dividends = add(tax_unit, period, ["dividend_income"])
        short_term_loss_applied = tax_unit(
            "ma_short_term_loss_against_dividends", period
        )
        cap = parameters(
            period
        ).gov.states.ma.tax.income.capital_gains.deductible_against_interest_dividends
        remaining_cap = max_(0, min_(dividends, cap) - short_term_loss_applied)
        return min_(remaining_cap, remaining_long_term_loss)
