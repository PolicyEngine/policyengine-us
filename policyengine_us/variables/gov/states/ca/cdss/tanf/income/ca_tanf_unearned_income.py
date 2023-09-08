from policyengine_us.model_api import *


class ca_tanf_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Other Unearned Income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
