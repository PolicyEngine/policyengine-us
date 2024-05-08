from policyengine_us.model_api import *


class co_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    adds = ["co_ccap_subsidy"]
    exhaustive_parameter_dependencies = "gov.states.co.ccap"
