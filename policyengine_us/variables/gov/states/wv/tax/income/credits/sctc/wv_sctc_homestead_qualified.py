from policyengine_us.model_api import *


class wv_sctc_homestead_qualified(Variable):
    """Actual exemption qualification for the property-tax cohort.

    Includes statutory age or certified disability, title, residence and occupancy.
    Its availability is reported separately from a known negative qualification.
    """

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    label = "West Virginia SCTC homestead qualifies for the exemption"
    reference = (
        "https://code.wvlegislature.gov/11-6B-2/",
        "https://code.wvlegislature.gov/11-6B-3/",
        "https://code.wvlegislature.gov/11-21-21/",
    )
    defined_for = StateCode.WV
