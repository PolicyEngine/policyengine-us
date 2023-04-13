from policyengine_us.model_api import *


class ut_total_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "Utah total dependents"
    unit = USD
    documentation = "Form TC-40, line 2c"
    definition_period = YEAR
    defined_for = StateCode.UT
    adds = ["ut_dependents_under_17", "ut_dependents_over_17"]
