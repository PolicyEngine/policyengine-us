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
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # Part C gross income nets all short-term losses against long-term
        # gains. Schedule B applies a short-term loss first against up to
        # $2,000 of dividends (line 20), so only the rest offsets long-term
        # gains (line 22).
        part_c_gross_income = tax_unit("ma_part_c_gross_income", period)
        long_term_capital_gains = add(tax_unit, period, ["long_term_capital_gains"])
        losses_against_dividends = tax_unit(
            "ma_short_term_loss_against_dividends", period
        )
        return min_(
            max_(0, long_term_capital_gains),
            part_c_gross_income + losses_against_dividends,
        )
