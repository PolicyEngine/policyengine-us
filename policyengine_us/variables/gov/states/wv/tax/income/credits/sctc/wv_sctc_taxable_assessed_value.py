from policyengine_us.model_api import *


class wv_sctc_taxable_assessed_value(Variable):
    """Full post-exemption value for one qualifying bill cohort, before the SCTC cap."""

    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    quantity_type = STOCK
    unit = USD
    default_value = -1
    label = "West Virginia SCTC full taxable assessed value"
    reference = "https://code.wvlegislature.gov/11-21-21/"
    defined_for = StateCode.WV
