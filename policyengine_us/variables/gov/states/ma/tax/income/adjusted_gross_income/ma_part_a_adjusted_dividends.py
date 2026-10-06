from policyengine_us.model_api import *


class ma_part_a_adjusted_dividends(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A adjusted interest and dividends"
    documentation = (
        "Massachusetts Schedule B, line 33: dividends less the short-term "
        "(line 20) and long-term (line 32) losses applied against them."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://taxsim.nber.org/historical_state_tax_forms/MA/2024/dor-2024-inc-sch-b-(form-1).pdf#page=2"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        dividends = add(tax_unit, period, ["dividend_income"])
        losses_applied = add(
            tax_unit,
            period,
            [
                "ma_short_term_loss_against_dividends",
                "ma_long_term_loss_against_dividends",
            ],
        )
        return max_(0, dividends - losses_applied)
