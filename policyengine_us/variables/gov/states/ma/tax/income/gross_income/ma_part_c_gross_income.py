from policyengine_us.model_api import *


class ma_part_c_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part C gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2"  # (b)(3)
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # Long-term capital gains
        ltcg = add(tax_unit, period, ["long_term_capital_gains"])
        # Short-term capital gains (can be negative)
        stcg = add(tax_unit, period, ["short_term_capital_gains"])
        # Per MA Schedule B line 22, short-term losses offset long-term gains
        stcg_losses = min_(0, stcg)
        return max_(0, ltcg + stcg_losses)
