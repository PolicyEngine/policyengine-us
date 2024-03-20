from policyengine_us.model_api import *


class sc_tanf_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "SC TANF unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
