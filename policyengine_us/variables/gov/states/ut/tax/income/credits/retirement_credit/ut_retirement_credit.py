from policyengine_us.model_api import *


class ut_retirement_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah retirement credit"
    unit = USD
    definition_period = YEAR
    defined_for = "ut_claims_retirement_credit"

    adds = ["ut_retirement_credit_max"]
