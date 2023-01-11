from policyengine_us.model_api import *


class ut_taxpayer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "UT taxpayer credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    adds = ["ut_taxpayer_credit_max"]
    subtracts = ["ut_taxpayer_credit_reduction"]
