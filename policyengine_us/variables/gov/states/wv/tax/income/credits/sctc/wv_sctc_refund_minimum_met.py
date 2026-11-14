from policyengine_us.model_api import *


class wv_sctc_refund_minimum_met(Variable):
    """Diagnostic only; this does not settle the return's refund or tax offsets."""

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "West Virginia SCTC meets the statutory refund minimum"
    reference = "https://code.wvlegislature.gov/11-21-21/"
    defined_for = StateCode.WV

    def formula_2025_01_01(tax_unit, period, parameters):
        available = tax_unit("wv_sctc_amount_available", period)
        amount = tax_unit("wv_sctc", period)
        p = parameters(period).gov.states.wv.tax.income.credits.sctc
        return available & (amount >= p.refund_minimum)
