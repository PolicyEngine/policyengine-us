from policyengine_us.model_api import *


class ma_part_c_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part C AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2",
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2024/dor-2024-inc-sch-b-(form-1).pdf#page=2",
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2023/dor-2023-inc-sch-d-(form-1).pdf",
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # Schedule B applies a short-term loss first against up to $2,000 of
        # dividends (line 20). Only the rest (line 21) offsets long-term
        # gains (line 22 and Schedule D, lines 14 and 15).
        short_term_capital_gains = add(tax_unit, period, ["short_term_capital_gains"])
        short_term_capital_loss = max_(0, -short_term_capital_gains)
        loss_against_dividends = tax_unit(
            "ma_short_term_loss_against_dividends", period
        )
        remaining_short_term_loss = short_term_capital_loss - loss_against_dividends
        long_term_capital_gains = add(tax_unit, period, ["long_term_capital_gains"])
        return max_(0, long_term_capital_gains - remaining_short_term_loss)
