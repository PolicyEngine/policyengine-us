from policyengine_us.model_api import *


class ut_total_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "Utah total dependents"
    unit = USD
    documentation = "Form TC-40, line 2c"
    definition_period = YEAR
    defined_for = StateCode.UT
    adds = ["tax_unit_count_dependents"]
