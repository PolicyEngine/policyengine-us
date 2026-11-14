from policyengine_us.model_api import *


class wv_sctc_income_facts_available(Variable):
    """Confirm current-year AGI, legal family count and actual federal AMT liability.

    A model's default AGI or AMT zero does not establish this receipt. For a
    nonfiler, the AGI-equivalent calculation must also have been verified.
    """

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    label = "West Virginia SCTC income and federal AMT facts are confirmed"
    reference = "https://code.wvlegislature.gov/11-21-21/"
    defined_for = StateCode.WV
