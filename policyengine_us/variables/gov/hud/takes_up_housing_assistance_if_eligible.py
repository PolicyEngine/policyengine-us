from policyengine_us.model_api import *


class takes_up_housing_assistance_if_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Whether an eligible SPM unit takes up housing assistance"
    definition_period = YEAR
    default_value = True
