from policyengine_us.model_api import *


class hud_utility_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD utility allowance"
    unit = USD
    documentation = "Utility allowance for HUD programs"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/982.517"
