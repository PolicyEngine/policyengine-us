from policyengine_us.model_api import *


class ut_refundable_credits(Variable):
    """
    Line 38 on Utah 2022 Individual Income Tax return form TC-40. These
    credits include the following categories and are listed at
    https://incometax.utah.gov/credits with their accompanying codes.
    * 39: Renewable commercial energy systems credit
    * 41: Special needs adoption credit
    * 47: Agricultural off-highway gas/undyed diesel credit
    * 48: Farm operation hand tools credit
    """

    value_type = float
    entity = TaxUnit
    label = "UT refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
