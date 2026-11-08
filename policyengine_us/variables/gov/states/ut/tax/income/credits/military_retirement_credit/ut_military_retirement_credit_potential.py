from policyengine_us.model_api import *


class ut_military_retirement_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah military retirement credit"
    unit = USD
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1043.html"
    defined_for = "ut_military_retirement_credit_eligible"

    adds = ["ut_military_retirement_credit_max"]
