from policyengine_us.model_api import *


class wv_sctc_homestead_facts_available(Variable):
    """Whether the cohort's homestead qualification, positive or negative, is known."""

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    label = "West Virginia SCTC homestead qualification is confirmed"
    reference = "https://code.wvlegislature.gov/11-21-21/"
    defined_for = StateCode.WV
