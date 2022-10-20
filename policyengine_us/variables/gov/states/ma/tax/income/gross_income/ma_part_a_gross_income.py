from policyengine_us.model_api import *


class ma_part_a_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        non_ma_interest = (
            0  # All interest assumed to be from banks with a presence in MA.
        )
        dividends = add(tax_unit, period, ["dividend_income"])
        short_term_capital_gains = max_(
            0, add(tax_unit, period, ["short_term_capital_gains"])
        )
        return non_ma_interest + dividends + short_term_capital_gains
