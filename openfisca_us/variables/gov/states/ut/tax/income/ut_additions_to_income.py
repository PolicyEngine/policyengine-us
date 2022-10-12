from policyengine_us.model_api import *


class ut_additions_to_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "UT additions to income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
