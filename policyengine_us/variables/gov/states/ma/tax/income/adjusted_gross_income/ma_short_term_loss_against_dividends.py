from policyengine_us.model_api import *


class ma_short_term_loss_against_dividends(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA short-term capital losses applied against dividends"
    documentation = (
        "Massachusetts Schedule B, line 20. Interest is treated as interest "
        "from Massachusetts banks (5.0% income), so line 9 is the dividends."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # (c)(2)(a) and (c)(4)
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section2",
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2024/dor-2024-inc-sch-b-(form-1).pdf#page=2",
        "https://www.mass.gov/doc/2024-form-1-instructions/download#page=25",
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        short_term_capital_gains = add(tax_unit, period, ["short_term_capital_gains"])
        short_term_capital_loss = max_(0, -short_term_capital_gains)
        dividends = add(tax_unit, period, ["dividend_income"])
        cap = parameters(
            period
        ).gov.states.ma.tax.income.capital_gains.deductible_against_interest_dividends
        return min_(cap, min_(dividends, short_term_capital_loss))
