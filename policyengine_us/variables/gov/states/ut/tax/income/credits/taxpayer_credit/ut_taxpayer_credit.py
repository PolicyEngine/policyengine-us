from policyengine_us.model_api import *


class ut_taxpayer_credit(Variable):
    """
    Line 20 of Utah 2022 Individual Income Tax return form TC-40.
    """

    value_type = float
    entity = TaxUnit
    label = "UT taxpayer credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    adds = ["ut_taxpayer_credit_max"]
    subtracts = ["ut_taxpayer_credit_reduction"]
