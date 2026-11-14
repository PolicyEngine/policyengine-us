from policyengine_us.model_api import *


class wv_sctc_input_missing(Variable):
    """Required facts for the SCTC amount remain unknown, not known ineligible."""

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "West Virginia SCTC amount is unavailable from the supplied facts"
    reference = "https://code.wvlegislature.gov/11-21-21/"
    defined_for = StateCode.WV

    def formula_2025_01_01(tax_unit, period, parameters):
        return ~tax_unit("wv_sctc_amount_available", period)
