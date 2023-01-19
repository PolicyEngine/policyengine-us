from policyengine_us.model_api import *


class co_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "CO TANF countable income"
    unit = USD
    definition_period = YEAR
    defined_for = "co_tanf_eligible"
