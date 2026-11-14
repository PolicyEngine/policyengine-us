from policyengine_us.model_api import *


class wv_sctc_family_unit_size(Variable):
    """Confirmed statutory family-unit residents, not an inferred tax-unit count."""

    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    default_value = 0
    label = "West Virginia SCTC family unit size"
    reference = "https://code.wvlegislature.gov/11-21-21/"
    defined_for = StateCode.WV
