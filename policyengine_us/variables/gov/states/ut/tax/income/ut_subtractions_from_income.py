from policyengine_us.model_api import *


class ut_subtractions_from_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "UT subtractions from income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
