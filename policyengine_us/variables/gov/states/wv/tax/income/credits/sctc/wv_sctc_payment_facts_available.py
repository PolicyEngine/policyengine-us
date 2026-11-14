from policyengine_us.model_api import *


class wv_sctc_payment_facts_available(Variable):
    """Confirm a complete fully paid cohort with one uniform taxable-value base.

    The full value and paid principal must concern the same homestead and cohort,
    include coherent discounts and all levies, and contain no duplicate claim.
    Partial payments, mixed cohorts and nonuniform bases are outside this receipt.
    """

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    label = "West Virginia SCTC payment facts are confirmed"
    reference = "https://code.wvlegislature.gov/11-21-21/"
    defined_for = StateCode.WV
