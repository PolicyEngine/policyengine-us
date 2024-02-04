from policyengine_us.model_api import *


class hud_gross_rent(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD gross rent"
    unit = USD
    documentation = "Gross rent for HUD programs"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/982.503"

    adds = ["pre_subsidy_rent", "hud_utility_allowance"]
