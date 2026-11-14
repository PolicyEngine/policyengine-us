from policyengine_us.model_api import *


class wv_sctc_amount_available(Variable):
    """A proved disqualifier establishes zero without requiring payment facts."""

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "West Virginia SCTC amount can be determined"
    reference = "https://code.wvlegislature.gov/11-21-21/"
    defined_for = StateCode.WV

    def formula_2025_01_01(tax_unit, period, parameters):
        eligibility_known = tax_unit("wv_sctc_eligibility_available", period)
        eligible = tax_unit("wv_sctc_eligible", period)
        payment_known = tax_unit("wv_sctc_payment_inputs_available", period)
        return (eligibility_known & ~eligible) | (eligible & payment_known)
