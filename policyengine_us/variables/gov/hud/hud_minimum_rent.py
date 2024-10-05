from policyengine_us.model_api import *


class hud_minimum_rent(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD minimum rent"
    unit = USD
    documentation = "Minimum Rent for HUD programs"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/5.630#a_3"

    def formula(spm_unit, period, parameters):
        # Assume all Section 8. Public housing is $50.
        return 25
